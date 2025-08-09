from django.shortcuts import render
from rest_framework import permissions, generics
from .payment import create_payment, get_aamarpay_transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentTransaction, ActivityLog
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import requests

User = get_user_model()



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
        
        print(f"=== TRANSACTION VERIFICATION SUCCESS ===")
        print(f"Transaction data: {transaction_data}")
        
        # Extract transaction information
        pay_status = callback_data.get('pay_status', 'Unknown')
        amount = callback_data.get('amount', '0.00')
        
        # Convert amount to Decimal
        try:
            amount_decimal = Decimal(str(amount).replace(',', ''))
        except:
            amount_decimal = Decimal('0.00')
        
        # Determine transaction status
        if pay_status.lower() in ['successful', 'success', 'completed']:
            transaction_status = 'success'
        elif pay_status.lower() in ['failed', 'failure', 'error']:
            transaction_status = 'failed'
        else:
            transaction_status = 'initiated'
        
        # Try to find existing transaction or create new one
        payment_transaction = None
        try:
            # Try to find existing transaction
            payment_transaction = PaymentTransaction.objects.get(transaction_id=request_id)
            print(f"Found existing transaction: {payment_transaction}")
            
            # Update existing transaction
            payment_transaction.status = transaction_status
            payment_transaction.gateway_response = {
                'callback_data': callback_data,
                'transaction_verification': transaction_data,
                'verification_timestamp': timezone.now().isoformat()
            }
            payment_transaction.save()
            print(f"Updated transaction status to: {transaction_status}")
            
        except PaymentTransaction.DoesNotExist:
            print(f"Transaction {request_id} not found in database, creating new record")
            
            # Create new transaction record (without user for callback)
            payment_transaction = PaymentTransaction.objects.create(
                user=None,  # AamarPay callback doesn't have user context
                transaction_id=request_id,
                amount=amount_decimal,
                status=transaction_status,
                gateway_response={
                    'callback_data': callback_data,
                    'transaction_verification': transaction_data,
                    'verification_timestamp': timezone.now().isoformat()
                }
            )
            print(f"Created new transaction record: {payment_transaction}")
        
        # Log the activity
        try:
            ActivityLog.objects.create(
                user=None,  # No user context in callback
                action=f"Payment callback received - {transaction_status}",
                metadata={
                    'transaction_id': request_id,
                    'pay_status': pay_status,
                    'amount': str(amount),
                    'callback_method': request.method,
                    'callback_data': callback_data
                }
            )
        except Exception as log_error:
            print(f"Failed to create activity log: {log_error}")
        
        return Response({
            "message": "Payment verification successful",
            "request_id": request_id,
            "callback_data": callback_data,
            "transaction_verification": transaction_data,
            "status": "success",
            "transaction_saved": True,
            "transaction_status": transaction_status,
            "database_id": payment_transaction.id if payment_transaction else None
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


@api_view(["GET", "POST"])
def payment_fail(request):
    return Response({"message": "Payment failed!"})

@api_view(["GET", "POST"])
def payment_cancel(request):
    return Response({"message": "Payment was canceled!"})