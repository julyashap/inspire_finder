from django.contrib.auth import mixins
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from recommendations.forms import ItemForm
from recommendations.models import Item, Like


class ItemListView(generic.ListView):
    model = Item

    def get_queryset(self):
        query = self.request.GET.get('search')

        if self.request.user.is_authenticated:
            if query:
                self.queryset = Item.objects.filter(name__icontains=query).\
                    exclude(user=self.request.user)
            else:
                self.queryset = Item.objects.exclude(user=self.request.user)
        elif query:
            self.queryset = Item.objects.filter(name__icontains=query)

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_likes_list'] = Like.objects.filter(user=self.request.user).values_list('item_id', flat=True)
        return context


class UserItemListView(mixins.LoginRequiredMixin, generic.ListView):
    model = Item
    template_name = 'recommendations/user_item_list.html'

    def get_queryset(self):
        self.queryset = Item.objects.filter(user=self.request.user)
        return super().get_queryset()


class ItemDetailView(generic.DetailView):
    model = Item


class ItemCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('recommendations:user_item_list')

    def form_valid(self, form):
        item = form.save()
        item.user = self.request.user
        item.save()
        return super().form_valid(form)


class ItemUpdateView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.UpdateView):
    model = Item
    form_class = ItemForm

    def test_func(self):
        return self.request.user == self.object.user

    def get_success_url(self):
        return reverse('recommendations:item_detail', kwargs={'pk': self.object.pk})


class ItemDeleteView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.DeleteView):
    model = Item
    success_url = reverse_lazy('recommendations:user_item_list')

    def test_func(self):
        return self.request.user == self.object.user


@login_required
def like_item(request, pk):
    item = Item.objects.get(pk=pk)
    like = Like.objects.create(user=request.user, item=item)
    like.save()
    return redirect(reverse('recommendations:item_list'))


@login_required
def unlike_item(request, pk):
    item = Item.objects.get(pk=pk)
    like = Like.objects.filter(user=request.user, item=item)
    like.delete()
    return redirect(reverse('recommendations:item_list'))


class UserLikeListView(mixins.LoginRequiredMixin, generic.ListView):
    model = Item
    template_name = 'recommendations/user_like_list.html'

    def get_queryset(self):
        self.queryset = Item.objects.filter(like__user=self.request.user)
        return super().get_queryset()
