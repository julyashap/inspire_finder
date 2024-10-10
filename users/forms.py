import re
from django.contrib.auth import forms as auth_forms
from users.models import User
from django import forms


class UserRegistrationForm(auth_forms.UserCreationForm):
    """Класс формы для регистрации (создания) пользователя"""

    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['phone'].help_text = 'Номер телефона должен начинаться с "+7" или с "8" и содержать всего 11 цифр.'

    def clean_phone(self):
        cleaned_data = self.cleaned_data.get('phone')

        if not re.match(r'^(8\d{10}|\+7\d{10})$', cleaned_data):
            raise auth_forms.ValidationError('Номер телефона должен начинаться с "+7" или "8" '
                                             'и содержать далее 10 цифр!')

        return cleaned_data


class UserUpdateForm(auth_forms.UserChangeForm):
    """Класс формы для обновления данных пользователя"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar', 'city',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()
        self.fields['phone'].help_text = 'Номер телефона должен начинаться с "+7" или с "8" и содержать всего 11 цифр.'

    def clean_phone(self):
        cleaned_data = self.cleaned_data.get('phone')

        if not re.match(r'^(8\d{10}|\+7\d{10})$', cleaned_data):
            raise auth_forms.ValidationError('Номер телефона должен начинаться с "+7" или "8" '
                                             'и содержать далее 10 цифр!')

        return cleaned_data


class PhoneConfirmForm(forms.Form):
    """Класс формы для ввода кода подтверждения с телефона"""

    code = forms.CharField(max_length=4, label='Код подтверждения')
