from django import forms
from recommendations.models import Item


class ItemForm(forms.ModelForm):
    stop_words = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево', 'бесплатно', 'обман', 'полиция', 'радар',
                  'реклама', 'ставки', 'кредит', 'займ', 'долг', 'алкоголь', 'наркотики', 'порнография']

    class Meta:
        model = Item
        fields = ('name', 'description', 'picture',)

    def clean_name(self):
        cleaned_data = self.cleaned_data.get('name')

        for stop_word in self.stop_words:
            if stop_word in cleaned_data.lower() or cleaned_data.lower() in stop_word:
                raise forms.ValidationError('Такое название недопустимо!')

        return cleaned_data

    def clean_description(self):
        cleaned_data = self.cleaned_data.get('description')

        for stop_word in self.stop_words:
            if stop_word in cleaned_data.lower() or cleaned_data.lower() in stop_word:
                raise forms.ValidationError('Такое описание недопустимо!')

        return cleaned_data
