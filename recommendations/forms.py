from django import forms
from recommendations.models import Item

STOP_WORDS = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево', 'бесплатно', 'обман', 'полиция', 'радар',
              'реклама', 'ставки', 'кредит', 'займ', 'долг', 'алкоголь', 'наркотики', 'порнография']


class ItemForm(forms.ModelForm):
    """Класс формы для создания и обновления экземпляров модели Item"""

    class Meta:
        model = Item
        fields = ('name', 'description', 'picture', 'category',)

    def clean_name(self):
        cleaned_data = self.cleaned_data.get('name')

        for stop_word in STOP_WORDS:
            if stop_word in cleaned_data.lower() or cleaned_data.lower() in stop_word:
                raise forms.ValidationError(f'Слово "{stop_word}" недопустимо в названии!')

        return cleaned_data

    def clean_description(self):
        cleaned_data = self.cleaned_data.get('description')

        for stop_word in STOP_WORDS:
            if stop_word in cleaned_data.lower() or cleaned_data.lower() in stop_word:
                raise forms.ValidationError(f'Слово "{stop_word}" недопустимо в описании!')

        return cleaned_data


class ContactsForm(forms.Form):
    """Класс формы для отправки сообщения модераторам"""

    email = forms.EmailField(label='Введите Ваш email')
    message = forms.CharField(
        label='',
        max_length=200,
        widget=forms.Textarea(attrs={
            'placeholder': 'Введите Ваше сообщение здесь...',
            'class': 'form-control',
            'rows': 5,
        }),
        required=True
    )

    def clean_message(self):
        cleaned_data = self.cleaned_data.get('message')

        for stop_word in STOP_WORDS:
            if stop_word in cleaned_data.lower() or cleaned_data.lower() in stop_word:
                raise forms.ValidationError(f'Слово "{stop_word}" недопустимо в сообщении!')

        return cleaned_data
