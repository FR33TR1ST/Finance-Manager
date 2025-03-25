from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .forms import TransactionForm, TableVariable, CreateAccountForm
from .models import Transaction, Account, Category, Type
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
import json
from datetime import datetime
from django.utils.timezone import now
import requests


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')


class CustomLoginOrMainView(TemplateView):
    template_name_login = 'login.html'
    template_name_main = 'main_page.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            return self.main_page(request, *args, **kwargs)
        else:
            return self.login_page(request, *args, **kwargs)

    def login_page(self, request, *args, **kwargs):
        # Render the login view
        if request.method == 'POST':
            login_view = LoginView.as_view(
                template_name=self.template_name_login,
                redirect_authenticated_user=self.redirect_authenticated_user,
                success_url=reverse_lazy('main')
            )
            return login_view(request, *args, **kwargs)
        return self.render_to_response({'template_name': self.template_name_login})

    def main_page(self, request, *args, **kwargs):
        # Fetch API data for dollar rates
        url_tarjeta = 'https://dolarapi.com/v1/dolares/tarjeta'
        url_blue = 'https://dolarapi.com/v1/dolares/blue'

        # Default values in case of an error
        tarjeta_compra, tarjeta_venta = 'N/A', 'N/A'
        blue_compra, blue_venta = 'N/A', 'N/A'

        try:
            # Fetching data from APIs
            response_tarjeta = requests.get(url_tarjeta)
            response_blue = requests.get(url_blue)

            if response_tarjeta.status_code == 200:
                data_tarjeta = response_tarjeta.json()
                tarjeta_compra = data_tarjeta.get("compra", "N/A")
                tarjeta_venta = data_tarjeta.get("venta", "N/A")

            if response_blue.status_code == 200:
                data_blue = response_blue.json()
                blue_compra = data_blue.get("compra", "N/A")
                blue_venta = data_blue.get("venta", "N/A")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching API data: {e}")

        # Prepare the context
        context = {
            'username': request.user.first_name,
            'tarjeta_compra': tarjeta_compra,
            'tarjeta_venta': tarjeta_venta,
            'blue_compra': blue_compra,
            'blue_venta': blue_venta,
        }
        return self.render_to_response(context)

    def get_template_names(self):
        # Dynamically choose the template based on authentication status
        return [self.template_name_main if self.request.user.is_authenticated else self.template_name_login]



class ManageTransactionView(LoginRequiredMixin, FormView):
    template_name = 'MTransactions.html'
    form_class = TransactionForm

    def get_form_kwargs(self):
        """
        Override to pass the logged-in user to the form's kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the logged-in user to the form
        return kwargs

    def form_valid(self, form):
        # Save the transaction with the current user
        new_transaction = form.save(commit=False)
        new_transaction.user = self.request.user  # Assign the current user
        if new_transaction.type.name == 'Debit':
            new_transaction.amount = -new_transaction.amount
        # Get the account associated with the transaction and update its balance
        acc_balance = Account.objects.get(id=new_transaction.account.id, user=self.request.user)  # Filter by user
        acc_balance.balance += new_transaction.amount
        new_transaction.current_amount = acc_balance.balance
        acc_balance.save()
        new_transaction.save()
        return redirect('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter transactions by the logged-in user
        context['table'] = Transaction.objects.filter(user=self.request.user)
        return context


class CreateAccountView(LoginRequiredMixin, FormView):
    template_name = 'CreateAccount.html'
    form_class = CreateAccountForm

    def form_valid(self, form):
        # Save the account with the current user
        new_account = form.save(commit=False)
        new_account.user = self.request.user  # Assign the current user
        new_account.save()
        return redirect('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter accounts by the logged-in user
        context['accounts'] = Account.objects.filter(user=self.request.user)
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
        # Filter transactions by the logged-in user
        context['table'] = Transaction.objects.filter(user=self.request.user)
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
        # Filter accounts by the logged-in user
        context['accounts'] = Account.objects.filter(user=self.request.user)
        return context


class SpecificBalanceView(LoginRequiredMixin, FormView):
    template_name = 'SpecificBalance.html'
    form_class = TableVariable

    def get(self, request, account=None, currency=None, *args, **kwargs):
        # Filter account and transactions by the logged-in user
        account_instance = get_object_or_404(Account, name=account, currency=currency, user=request.user)
        self.account_balance = Transaction.objects.filter(account=account_instance)
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


class AnalysisView(LoginRequiredMixin, View):
    template_name = 'transactions_analytics.html'

    def get(self, request, *args, **kwargs):
        # Get filters from the request
        time_filter = request.GET.get('time_filter', 'day')  # Default to day
        start_date = request.GET.get('start_date', '2003-12-12')
        end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))

        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Filter transactions by date range and user
        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Timeline aggregation (cumulative)
        if time_filter == 'day':
            timeline_data = (
                transactions.annotate(period=F('date'))
                .values('period')
                .annotate(total=Sum('amount'))
                .order_by('period')
            )
        elif time_filter == 'year':
            timeline_data = (
                transactions.annotate(period=F('date__year'))
                .values('period')
                .annotate(total=Sum('amount'))
                .order_by('period')
            )
        else:  # Default to month
            timeline_data = (
                transactions.annotate(period=F('date__month'))
                .values('period')
                .annotate(total=Sum('amount'))
                .order_by('period')
            )

        # Calculate cumulative totals
        cumulative_total = 0
        cumulative_timeline = []
        for data in timeline_data:
            cumulative_total += data['total']
            cumulative_timeline.append({
                'period': str(data['period']),
                'total': float(data['total']),
                'cumulative': float(cumulative_total)
            })

        # Aggregate by category
        categories = (
            transactions.values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        categories = [{'name': category['category__name'], 'total': float(category['total'])} for category in categories]
        extra_colors = [
            '#4caf50', '#f44336', '#2196f3', '#ff9800', '#9c27b0',
            "#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3",
            "#03a9f4", "#00bcd4", "#009688", "#4caf50", "#8bc34a",
            "#cddc39", "#ffeb3b", "#ffc107", "#ff9800", "#ff5722",
            "#795548", "#9e9e9e", "#607d8b", "#ffb74d", "#ff8a65",
            "#f48fb1", "#ce93d8", "#b39ddb", "#90caf9", "#80deea"
        ]
        # Prepare chart data
        category_chart_data = json.dumps({
            'labels': [category['name'] for category in categories],
            'datasets': [{
                'data': [category['total'] for category in categories],
                'backgroundColor': extra_colors[:len(categories)],
            }]
        })

        timeline_chart_data = json.dumps({
            'labels': [data['period'] for data in cumulative_timeline],
            'datasets': [
                {
                    'label': 'Daily Total',
                    'data': [data['total'] for data in cumulative_timeline],
                    'backgroundColor': '#2196f3',
                    'borderColor': '#2196f3',
                    'fill': False,
                },
                {
                    'label': 'Cumulative Total',
                    'data': [data['cumulative'] for data in cumulative_timeline],
                    'backgroundColor': '#4caf50',
                    'borderColor': '#4caf50',
                    'fill': False,
                }
            ]
        })

        return render(request, self.template_name, {
            'category_chart_data': category_chart_data,
            'timeline_chart_data': timeline_chart_data,
            'time_filter': time_filter,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        })
