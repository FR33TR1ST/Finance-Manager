from django.urls import path
from .views import (
    CustomLoginOrMainView,
    ManageTransactionView,
    SearchTransactionsView,
    BalanceView,
    SpecificBalanceView,
    LogoutView,
    AnalysisView
)
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', CustomLoginOrMainView.as_view(), name='main'),
    path('transaction/', ManageTransactionView.as_view(), name='mtransaction'),
    path('stransaction/', SearchTransactionsView.as_view(), name='stransaction'),
    path('balance/', BalanceView.as_view(), name='balance'),
    path('balance/<str:account>/<str:currency>/', SpecificBalanceView.as_view(), name='sbalance'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('analytics/', AnalysisView.as_view(), name='analytics'),
]
