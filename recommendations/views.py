from django.contrib.auth import mixins
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from recommendations.forms import ItemForm
from recommendations.models import Item, Like, Category
from recommendations.services import collaborative_filtering_alg, NOW, get_statistics
from users.models import User


class CategoryListView(generic.ListView):
    model = Category

    def get_queryset(self):
        query = self.request.GET.get('search')

        if query:
            self.queryset = Category.objects.filter(name__icontains=query)

        return super().get_queryset()


class UserItemListView(mixins.LoginRequiredMixin, generic.ListView):
    model = Item
    template_name = 'recommendations/user_item_list.html'

    def get_queryset(self):
        self.queryset = Item.objects.filter(user=self.request.user).order_by('-created_at')
        return super().get_queryset()


class UserLikeListView(mixins.LoginRequiredMixin, generic.ListView):
    model = Item
    template_name = 'recommendations/user_like_list.html'

    def get_queryset(self):
        user_likes = Like.objects.filter(user=self.request.user).order_by('-created_at'). \
            values_list('item_id', flat=True)

        self.queryset = Item.objects.filter(pk__in=user_likes)

        return super().get_queryset()


class ItemListView(generic.ListView):
    model = Item

    def get_queryset(self):
        query = self.request.GET.get('search')

        category_pk = self.kwargs.get('pk')
        category = Category.objects.get(pk=category_pk)

        category_published_items = Item.objects.filter(category=category).filter(is_published=True)

        if self.request.user.is_authenticated:
            if query:
                self.queryset = category_published_items. \
                    filter(name__icontains=query). \
                    exclude(user=self.request.user).order_by('-count_likes')
            else:
                self.queryset = category_published_items. \
                    exclude(user=self.request.user). \
                    order_by('-count_likes')
        else:
            if query:
                self.queryset = category_published_items. \
                    filter(name__icontains=query). \
                    order_by('-count_likes')
            else:
                self.queryset = category_published_items

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category_pk'] = self.kwargs.get('pk')
        if self.request.user.is_authenticated:
            context['user_likes_list'] = Like.objects.filter(user=self.request.user).values_list('item_id', flat=True)

        return context


class ItemDetailView(generic.DetailView):
    model = Item


class ItemCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('recommendations:user_item_list')

    def form_valid(self, form):
        item = form.save()
        item.user = self.request.user
        item.created_at = NOW
        item.save()
        return super().form_valid(form)


class ItemUpdateView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.UpdateView):
    model = Item
    form_class = ItemForm

    def test_func(self):
        return self.request.user == self.object.user

    def form_valid(self, form):
        item = form.save()
        item.updated_at = NOW
        item.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('recommendations:item_detail', kwargs={'pk': self.object.pk})


class ItemDeleteView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.DeleteView):
    model = Item
    success_url = reverse_lazy('recommendations:user_item_list')

    def test_func(self):
        return self.request.user == self.get_object().user


class LikeErrorView(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = 'recommanedations/like_error.html'


@login_required
def like_item(request, pk):
    previous_page = request.META.get('HTTP_REFERER')

    item = Item.objects.get(pk=pk)

    if item.user == request.user:
        return redirect(reverse('recommendations:like_error'))

    like = Like.objects.create(user=request.user, item=item)
    like.created_at = NOW
    item.count_likes += 1

    item.save()
    like.save()

    return redirect(previous_page)


@login_required
def unlike_item(request, pk):
    previous_page = request.META.get('HTTP_REFERER')

    item = Item.objects.get(pk=pk)
    like = Like.objects.filter(user=request.user, item=item)
    like.delete()

    item.count_likes -= 1
    item.save()

    if previous_page == request.build_absolute_uri(reverse('recommendations:statistic')) or \
            previous_page == request.build_absolute_uri(reverse('recommendations:item_recommended')):
        return redirect(reverse('recommendations:category_list'))

    return redirect(previous_page)


class RecommendedItemView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.TemplateView):
    template_name = 'recommendations/item_recommended.html'

    def test_func(self):
        return self.request.user.like_set.exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recommended_items_ids = collaborative_filtering_alg(self.request.user.pk)
        recommended_items = Item.objects.filter(pk__in=recommended_items_ids).order_by('-count_likes')

        context['object_list'] = recommended_items
        context['user_likes_list'] = Like.objects.filter(user=self.request.user).values_list('item_id', flat=True)

        return context


class StatisticView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.TemplateView):
    template_name = 'recommendations/statistic.html'

    def test_func(self):
        return self.request.user.like_set.exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        same_interest_users, most_popular_items = get_statistics(self.request.user.pk)
        same_interest_users = User.objects.filter(pk__in=same_interest_users)
        most_popular_items = Item.objects.filter(pk__in=most_popular_items).order_by('-count_likes')

        context['same_interest_users'] = same_interest_users
        context['most_popular_items'] = most_popular_items
        context['user_likes_list'] = Like.objects.filter(user=self.request.user).values_list('item_id', flat=True)

        return context
