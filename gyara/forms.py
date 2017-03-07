from django import forms
from django.forms import DateInput, DateField, inlineformset_factory, formset_factory, modelformset_factory, ChoiceField, \
    Select, ModelChoiceField

from gyara.models import Category, Transaction


class UploadFileForm(forms.Form):
    file = forms.FileField()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','flow']


class TransactionForm(forms.ModelForm):
    date = DateField(input_formats=["%d-%m-%Y"],widget=DateInput(attrs={'type':'date'},format="%d-%m-%Y"))
    category = ModelChoiceField(queryset=Category.objects,widget=Select(attrs={'class' : 'search'}))

    class Meta:
        model = Transaction
        fields = ('description', 'date','flow','category', 'value')


TransactionFormSet = modelformset_factory(model=Transaction,form=TransactionForm,fields=['description', 'date', 'flow','category','value'])