from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
import requests
from .forms import TransactionForm, TableVariable
from .models import Transaction, Account, Category, Type
from django.urls import reverse_lazy
# Create your views here.


class CustomLoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def main(request):
    username = request.user.first_name
    return render(request, 'main_page.html', context={'username': username})


@login_required
def mtransaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            new_transaction = form.save(commit=False)
            if new_transaction.type.name == 'Debit':
                new_transaction.amount = -new_transaction.amount
            acc_balance = Account.objects.get(id=new_transaction.account.id)
            acc_balance.balance += new_transaction.amount
            new_transaction.current_amount = acc_balance.balance
            acc_balance.save()
            new_transaction.save()
            return redirect('main')
    return render(request, 'MTransactions.html', {'form': TransactionForm(),
                                                  'table': Transaction.objects.all()})


@login_required
def stransactions(request):
    if request.method == 'POST':
        form = TableVariable(request.POST)
        if form.is_valid():
            form_values = {
                'date_value': form.cleaned_data['date_value'],
                'name_value': form.cleaned_data['name_value'],
                'type_value': form.cleaned_data['type_value'],
                'account_value': form.cleaned_data['account_value'],
                'amount_value': form.cleaned_data['amount_value'],
                'category_value': form.cleaned_data['category_value'],
                'description_value': form.cleaned_data['description_value'],
            }
            return render(request, 'STransactions.html', {'table': Transaction.objects.all(), 'form': form,
                                                           'form_values': form_values})
    else:
        form = TableVariable()
    return render(request, 'STransactions.html', {'table': Transaction.objects.all(),
                  'form': form, 'form_values': {'date_value': True, 'name_value': True,
                                                'type_value': True, 'account_value': True,
                                                'amount_value': True, 'category_value': True,
                                                'description_value': True}})


@login_required
def balance(request):
    accounts = Account.objects.all()
    return render(request, 'Balance.html', context={'accounts': accounts})


@login_required
def sbalance(request, account=None, currency=None):
    account_balance = Transaction.objects.filter(account=Account.objects.get(name=account, currency=currency).id)
    if request.method == 'POST':
        form = TableVariable(request.POST)
        if form.is_valid():
            form_values = {
                'date_value': form.cleaned_data['date_value'],
                'name_value': form.cleaned_data['name_value'],
                'type_value': form.cleaned_data['type_value'],
                'account_value': form.cleaned_data['account_value'],
                'amount_value': form.cleaned_data['amount_value'],
                'category_value': form.cleaned_data['category_value'],
                'description_value': form.cleaned_data['description_value']
            }
            return render(request, 'SpecificBalance.html', {'table': account_balance, 'account': account,
                                                            'form': form, 'form_values': form_values})
    else:
        form = TableVariable()
    return render(request, 'SpecificBalance.html', {'table': account_balance, 'account': account,
                                                    'form': form, 'form_values': {'date_value': True, 'name_value': True,
                                                                                  'type_value': True, 'account_value': True,
                                                                                  'amount_value': True, 'category_value': True,
                                                                                  'description_value': True}})
