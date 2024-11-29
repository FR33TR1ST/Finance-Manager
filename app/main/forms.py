from django import forms
from .models import Transaction, Account, Category, Type


class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    type = forms.ModelChoiceField(queryset=Type.objects.all())
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    amount = forms.DecimalField(max_digits=15, decimal_places=2)
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Description'}))

    class Meta:
        model = Transaction
        fields = ['date', 'name', 'type', 'account', 'amount', 'category', 'description']


class TableVariable(forms.Form):
    date_value = forms.BooleanField(required=False, label='Date')
    name_value = forms.BooleanField(required=False, label='Name')
    type_value = forms.BooleanField(required=False, label='Type')
    account_value = forms.BooleanField(required=False, label='Account')
    amount_value = forms.BooleanField(required=False, label='Amount')
    category_value = forms.BooleanField(required=False, label='Category')
    description_value = forms.BooleanField(required=False, label='Description')

    class Meta:
        fields = ['date_value', 'name_value', 'type_value', 'account_value', 'amount_value', 'category_value',
                  'description_value']
