from django.shortcuts import render
from rest_framework import permissions, generics
from .payment import create_payment, transaction_response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



class CreatePaymentView(generics.CreateAPIView):
      permission_classes = [permissions.IsAuthenticated]
      
      def post(self, request, *args, **kwargs):
            response = create_payment(request)
            if isinstance(response, JsonResponse):
                  return response
            else:
                  return JsonResponse({"message": "Payment created successfully!"}, status=200)


@csrf_exempt
def payment_success(request):
      response = transaction_response(request)
    return JsonResponse({"message": "Payment was successful!"})

@csrf_exempt
def payment_fail(request):
    return JsonResponse({"message": "Payment failed!"})


@csrf_exempt
def payment_cancel(request):
    return JsonResponse({"message": "Payment was canceled!"})