from django.contrib.auth import mixins
from django.urls import reverse_lazy, reverse
from django.views import generic
from users.forms import UserRegistrationForm, UserUpdateForm
from users.models import User
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView


class RegistrationView(generic.CreateView):
    model = User
    success_url = reverse_lazy('users:user_login')
    form_class = UserRegistrationForm


class LoginView(BaseLoginView):
    template_name = 'users/user_login.html'


class LogoutView(BaseLogoutView):
    pass


class UserDetailView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.DetailView):
    model = User

    def test_func(self):
        return self.request.user == self.get_object()


class UserUpdateView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm

    def test_func(self):
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.object.pk})


class UserDeleteView(mixins.LoginRequiredMixin, mixins.UserPassesTestMixin, generic.DeleteView):
    model = User
    success_url = reverse_lazy('recommendations:item_list')

    def test_func(self):
        return self.request.user == self.get_object()
