from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .forms import TransactionForm, TableVariable
from .models import Transaction, Account, Category, Type
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
import json
from datetime import datetime


class CustomLoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')


class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.first_name
        return context


class ManageTransactionView(LoginRequiredMixin, FormView):
    template_name = 'MTransactions.html'
    form_class = TransactionForm

    def form_valid(self, form):
        new_transaction = form.save(commit=False)
        if new_transaction.type.name == 'Debit':
            new_transaction.amount = -new_transaction.amount
        acc_balance = Account.objects.get(id=new_transaction.account.id)
        acc_balance.balance += new_transaction.amount
        new_transaction.current_amount = acc_balance.balance
        acc_balance.save()
        new_transaction.save()
        return redirect('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = Transaction.objects.all()
        return context


class SearchTransactionsView(LoginRequiredMixin, FormView):
    template_name = 'STransactions.html'
    form_class = TableVariable

    def form_valid(self, form):
        form_values = form.cleaned_data
        context = self.get_context_data(form_values=form_values)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = Transaction.objects.all()
        context['form_values'] = kwargs.get('form_values', {
            'date_value': True, 'name_value': True, 'type_value': True,
            'account_value': True, 'amount_value': True, 'category_value': True,
            'description_value': True
        })
        return context


class BalanceView(LoginRequiredMixin, TemplateView):
    template_name = 'Balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Account.objects.all()
        return context


class SpecificBalanceView(LoginRequiredMixin, FormView):
    template_name = 'SpecificBalance.html'
    form_class = TableVariable

    def get(self, request, account=None, currency=None, *args, **kwargs):
        account_instance = Account.objects.get(name=account, currency=currency)
        self.account_balance = Transaction.objects.filter(account=account_instance.id)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form_values = form.cleaned_data
        context = self.get_context_data(form_values=form_values)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = getattr(self, 'account_balance', None)
        context['account'] = self.kwargs.get('account')
        context['form_values'] = kwargs.get('form_values', {
            'date_value': True, 'name_value': True, 'type_value': True,
            'account_value': True, 'amount_value': True, 'category_value': True,
            'description_value': True
        })
        return context


class AnalysisView(View):
    template_name = 'transactions_analytics.html'

    def get(self, request, *args, **kwargs):
        # Get filters from the request
        time_filter = request.GET.get('time_filter', 'day')  # Default to month
        start_date = request.GET.get('start_date', '2003-12-12')
        end_date = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Filter transactions by date range
        transactions = Transaction.objects.filter(date__range=[start_date, end_date])

        # Timeline aggregation
        if time_filter == 'day':
            timeline_data = transactions.annotate(period=F('date')).values('period').annotate(total=Sum('amount')).order_by('period')
        elif time_filter == 'year':
            timeline_data = transactions.annotate(period=F('date__year')).values('period').annotate(total=Sum('amount')).order_by('period')
        else:  # Default to month
            timeline_data = transactions.annotate(period=F('date__month')).values('period').annotate(total=Sum('amount')).order_by('period')

        # Prepare timeline data
        timeline = [{'period': str(data['period']), 'total': float(data['total'])} for data in timeline_data]

        # Aggregate by category
        categories = (
            transactions.values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        categories = [{'name': category['category__name'], 'total': float(category['total'])} for category in categories]

        # Prepare chart data
        category_chart_data = json.dumps({
            'labels': [category['name'] for category in categories],
            'datasets': [{
                'data': [category['total'] for category in categories],
                'backgroundColor': ['#4caf50', '#f44336', '#2196f3', '#ff9800', '#9c27b0'],  # Add more colors if needed
            }]
        })

        timeline_chart_data = json.dumps({
            'labels': [data['period'] for data in timeline],
            'datasets': [{
                'label': 'Total Amount',
                'data': [data['total'] for data in timeline],
                'backgroundColor': '#4caf50',
                'borderColor': '#4caf50',
                'fill': False,
            }]
        })

        return render(request, self.template_name, {
            'category_chart_data': category_chart_data,
            'timeline_chart_data': timeline_chart_data,
            'time_filter': time_filter,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        })


