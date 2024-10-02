from django.contrib.auth import forms
from users.models import User
from django.forms import HiddenInput


class UserRegistrationForm(forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2',)


class UserUpdateForm(forms.UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar', 'country',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = HiddenInput()
