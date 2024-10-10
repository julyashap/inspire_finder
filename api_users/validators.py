import re
from rest_framework.exceptions import ValidationError


class PhoneValidator:
    """Класс валидатора номера телефона"""

    def __call__(self, value):
        phone = dict(value).get('phone')

        if phone and not re.match(r'^(8\d{10}|\+7\d{10})$', phone):
            raise ValidationError('Номер телефона должен начинаться с "+7" или "8" и содержать далее 10 цифр!')
