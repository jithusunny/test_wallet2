from django.urls import path

from api import views

urlpatterns = [
    path('init', views.wallet_init, name='wallet_init'),
    path('wallet', views.wallet, name='wallet'),
    path('wallet/deposits', views.deposit, name='deposit'),
    path('wallet/withdrawals', views.withdraw, name='withdraw'),
]
