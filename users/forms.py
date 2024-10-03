import re
from django.contrib.auth import forms
from users.models import User
from django.forms import HiddenInput


class UserRegistrationForm(forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['phone'].help_text = 'Номер телефона должен начинаться с "+7" или с "8" и содержать всего 11 цифр.'

    def clean_phone(self):
        cleaned_data = self.cleaned_data.get('phone')

        if not re.match(r'^(8\d{10}|\+7\d{10})$', cleaned_data):
            raise forms.ValidationError('Номер телефона должен начинаться с "+7" или "8" и содержать далее 10 цифр!')

        return cleaned_data


class UserUpdateForm(forms.UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar', 'city',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = HiddenInput()
        self.fields['phone'].help_text = 'Номер телефона должен начинаться с "+7" или с "8" и содержать всего 11 цифр.'

    def clean_phone(self):
        cleaned_data = self.cleaned_data.get('phone')

        if not re.match(r'^(8\d{10}|\+7\d{10})$', cleaned_data):
            raise forms.ValidationError('Номер телефона должен начинаться с "+7" или "8" и содержать далее 10 цифр!')

        return cleaned_data
