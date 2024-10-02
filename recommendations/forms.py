from django import forms
from recommendations.models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'description', 'picture',)
