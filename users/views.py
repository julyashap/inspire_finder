import requests
from django.contrib.auth import mixins
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views import generic
from config import settings
from users.forms import UserRegistrationForm, UserUpdateForm, PhoneConfirmForm
from users.models import User
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView


class RegistrationView(generic.CreateView):
    model = User
    success_url = reverse_lazy('users:phone_confirm')
    form_class = UserRegistrationForm

    def form_valid(self, form):
        code = get_random_string(length=4)

        user = form.save()
        user.code = code
        user.is_active = False
        user.save()

        requests.get(f"https://{settings.SMSAERO_EMAIL}:{settings.SMSAERO_API_KEY}@gate.smsaero.ru/v2/sms/"
                     f"send?number={user.phone}&text=Код+подтверждения:+{code}&sign=SMS Aero")

        return super().form_valid(form)


def phone_confirm(request):
    if request.method == 'POST':
        form = PhoneConfirmForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, code=form.cleaned_data['code'])
            user.is_active = True
            user.save()
            return redirect(reverse('users:user_login'))

    elif request.method == 'GET':
        form = PhoneConfirmForm()

    return render(request, 'users/phone_confirm.html', {'form': form})


class LoginView(BaseLoginView):
    template_name = 'users/user_login.html'


class LogoutView(BaseLogoutView):
    pass


class UserDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_user'] = self.request.user

        return context


class UserUpdateView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm

    def test_func(self):
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.object.pk})


class UserDeleteView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.DeleteView):
    model = User
    success_url = reverse_lazy('recommendations:category_list')

    def test_func(self):
        return self.request.user == self.get_object()
