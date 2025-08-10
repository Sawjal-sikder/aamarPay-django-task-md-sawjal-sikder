from rest_framework import permissions, generics, status
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
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import FileUpload
from .serializer import FileUploadSerializer, PaymentTransactionSerializer, ActivityLogSerializer
from .task import process_file_task

User = get_user_model()



class CreatePaymentView(generics.CreateAPIView):
      permission_classes = [permissions.IsAuthenticated]
      
      def post(self, request, *args, **kwargs):
                        
            response = create_payment(request)
            
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
    
    
    # Handle case where request_id might be a list
    if isinstance(request_id, list):
        request_id = request_id[0] if request_id else None
    
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
        
        
        # Extract transaction information
        pay_status = callback_data.get('pay_status', 'Unknown')
        amount = callback_data.get('amount', '0.00')
        
        # Handle case where pay_status might be a list
        if isinstance(pay_status, list):
            pay_status = pay_status[0] if pay_status else 'Unknown'
        
        # Handle case where amount might be a list
        if isinstance(amount, list):
            amount = amount[0] if amount else '0.00'
        
        # Convert amount to Decimal
        try:
            amount_decimal = Decimal(str(amount).replace(',', ''))
        except:
            amount_decimal = Decimal('0.00')
        
        # Determine transaction status
        if str(pay_status).lower() in ['successful', 'success', 'completed']:
            transaction_status = 'success'
        elif str(pay_status).lower() in ['failed', 'failure', 'error']:
            transaction_status = 'failed'
        else:
            transaction_status = 'initiated'
        
        # Try to find existing transaction or create new one
        payment_transaction = None
        try:
            # Try to find existing transaction
            payment_transaction = PaymentTransaction.objects.get(transaction_id=request_id)
            
            # Update existing transaction
            payment_transaction.status = transaction_status
            payment_transaction.gateway_response = {
                'callback_data': callback_data,
                'transaction_verification': transaction_data,
                'verification_timestamp': timezone.now().isoformat()
            }
            payment_transaction.save()
            
        except PaymentTransaction.DoesNotExist:
            
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
        return Response({
            "error": f"Transaction verification failed: {str(e)}",
            "request_id": request_id,
            "callback_data": callback_data
        }, status=500)
    except ValueError as e:

        return Response({
            "error": "Invalid response from payment gateway",
            "request_id": request_id,
            "callback_data": callback_data
        }, status=500)


def payment_fail(request):
    return Response({"message": "Payment failed!"})

def payment_cancel(request):
    return Response({"message": "Payment was canceled!"})



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request):
    # Check if user has a successful payment
    has_paid = PaymentTransaction.objects.filter(user=request.user, status='success').exists()
    if not has_paid:
        # For API, better return a JSON response, not redirect
        return Response(
            {"detail": "Payment required before uploading files.", "payment_url": "/api/initiate-payment/"},
            status=status.HTTP_402_PAYMENT_REQUIRED  # 402 Payment Required (informal)
        )

    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    if not file.name.endswith((".txt", ".docx")):
        return Response({"error": "Only .txt or .docx files allowed."}, status=status.HTTP_400_BAD_REQUEST)

    record = FileUpload.objects.create(
        user=request.user,
        file=file,
        filename=file.name,
        status="processing"
    )

    process_file_task.delay(record.id)

    return Response({"message": "File uploaded successfully and is being processed."}, status=status.HTTP_201_CREATED)


class FileUploadListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileUploadSerializer

    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user).order_by('-upload_time')

class PaymentTransactionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentTransactionSerializer

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by('-timestamp')
    
class ActivityLogListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user).order_by('-timestamp')