from django import forms
from .models import Transaction, Account, Category, Type


class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    type = forms.ModelChoiceField(queryset=Type.objects.all())
    account = forms.ModelChoiceField(queryset=Account.objects.none())  # Start with an empty queryset
    amount = forms.DecimalField(max_digits=15, decimal_places=2)
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Description'}))

    class Meta:
        model = Transaction
        fields = ['date', 'name', 'type', 'account', 'amount', 'category', 'description']

    def __init__(self, *args, **kwargs):
        # Extract the user from kwargs
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter the account queryset by the user's accounts
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
        else:
            self.fields['account'].queryset = Account.objects.none()


class CreateAccountForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    type = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type'}))
    currency = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Currency'}))
    balance = forms.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        model = Account
        fields = ['name', 'type', 'currency', 'balance']


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
