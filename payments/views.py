from django.shortcuts import render
from rest_framework import permissions, generics
from .payment import create_payment, get_aamarpay_transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests



class CreatePaymentView(generics.CreateAPIView):
      permission_classes = [permissions.IsAuthenticated]
      
      def post(self, request, *args, **kwargs):
                        
            response = create_payment(request)
            print("=== CREATE PAYMENT RESPONSE ===")
            print(f"response: {response}")
            
            if isinstance(response, JsonResponse):
                 
                  return response
            else:
                  return JsonResponse({"message": "Payment created successfully!"}, status=200)


@api_view(["GET", "POST"])
@permission_classes([])  # Remove authentication for AamarPay callbacks
def payment_success(request):
    
    request_id = None
    callback_data = {}
    
    if request.method == "GET":
        # Handle GET parameters (query params)
        callback_data = dict(request.GET)
        request_id = (
            request.GET.get("mer_txnid") or 
            request.GET.get("request_id") or 
            request.GET.get("tran_id") or
            request.GET.get("opt_a") or
            request.GET.get("opt_b")
        )
    
    elif request.method == "POST":
        # Handle POST data - Use request.data for DRF compatibility
        if hasattr(request, 'data') and request.data:
            callback_data = dict(request.data)
        else:
            callback_data = dict(request.POST)
        
        # Try to get request_id from different sources
        data_source = request.data if hasattr(request, 'data') else request.POST
        request_id = (
            data_source.get("mer_txnid") or 
            data_source.get("request_id") or 
            data_source.get("tran_id") or
            data_source.get("opt_a") or
            data_source.get("opt_b")
        )
    
    print(f"Extracted request_id: {request_id}")
    print(f"Callback data: {callback_data}")
    
    if not request_id:
        return Response({
            "error": "Missing request_id",
            "received_data": callback_data,
            "method": request.method,
            "help": "Expected mer_txnid, request_id, tran_id, opt_a, or opt_b"
        }, status=400)

    try:
        # Get transaction details from AamarPay
        transaction_data = get_aamarpay_transaction(request_id)
        
        
        return Response({
            "message": "Payment verification successful",
            "request_id": request_id,
            "callback_data": callback_data,
            "transaction_verification": transaction_data,
            "status": "success"
        })
        
    except requests.exceptions.RequestException as e:
        print(f"Transaction verification failed: {e}")
        return Response({
            "error": f"Transaction verification failed: {str(e)}",
            "request_id": request_id,
            "callback_data": callback_data
        }, status=500)
    except ValueError as e:
        print(f"Invalid response from AamarPay: {e}")
        return Response({
            "error": "Invalid response from payment gateway",
            "request_id": request_id,
            "callback_data": callback_data
        }, status=500)


def payment_fail(request):
    return JsonResponse({"message": "Payment failed!"})


def payment_cancel(request):
    return JsonResponse({"message": "Payment was canceled!"})