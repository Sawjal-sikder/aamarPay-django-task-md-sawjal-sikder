from django.urls import path
from .views import *

urlpatterns = [
    path('initiate-payment/', CreatePaymentView.as_view(), name='create_payment'),
    path('test-callback/', test_payment_callback, name='test_callback'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/fail/', payment_fail, name='payment_fail'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
]
