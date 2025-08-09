from django.urls import path
from .views import *

urlpatterns = [
    path('initiate-payment/', CreatePaymentView.as_view(), name='create_payment'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/fail/', payment_fail, name='payment_fail'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
]
