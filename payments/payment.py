from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import json
from urllib import request
import uuid
import requests
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from decimal import Decimal
# user model import User
from django.contrib.auth import get_user_model

User = get_user_model()

store_id = settings.AAMARPAY_STORE_ID
signature_key = settings.AAMARPAY_SIGNATURE_KEY
      
@csrf_exempt
@require_POST
@login_required
def create_payment(request):
      endpoint = settings.AAMARPAY_ENDPOINT
      
      success_url = request.build_absolute_uri(reverse(settings.SUCCESS_URL_NAME))
      fail_url = request.build_absolute_uri(reverse(settings.FAIL_URL_NAME))
      cancel_url = request.build_absolute_uri(reverse(settings.CANCEL_URL_NAME))

      tran_id = str(uuid.uuid4())
      
      
      user = request.user if request.user.is_authenticated else None
      

      if user:
            user_get = User.objects.get(id=user.id)
            
            cus_email = getattr(user_get, "email", None)
            if not cus_email:
                  cus_email = "anonymous@example.com"
            
            # Better name handling
            if hasattr(user_get, "get_full_name") and user_get.get_full_name():
                  cus_name = user_get.get_full_name()
            elif hasattr(user_get, "first_name") and user_get.first_name:
                  cus_name = user_get.first_name
            else:
                  cus_name = getattr(user_get, "username", "Anonymous User") or "Anonymous User"
      else:
            cus_name = "Anonymous User"
            cus_email = "anonymous@example.com"

      data = {
      "store_id": store_id,
      "tran_id": tran_id,
      "success_url": success_url,
      "fail_url": fail_url,
      "cancel_url": cancel_url,
      "amount": "100.00",
      "currency": "BDT",
      "signature_key": signature_key,
      "desc": "Test Payment ৳100",
      "cus_name": cus_name,
      "cus_email": cus_email,
      "cus_add1": "House B-158 Road 22",
      "cus_add2": "Mohakhali DOHS",
      "cus_city": "Dhaka",
      "cus_state": "Dhaka",
      "cus_postcode": "1206",
      "cus_country": "Bangladesh",
      "cus_phone": "+8801704000000",
      "type": "json"
      }

      print("=== PAYMENT REQUEST DATA ===")
      print(json.dumps(data, indent=4))
      print("=" * 50)
      
      # Create PaymentTransaction record
      try:
          from .models import PaymentTransaction
          payment_transaction = PaymentTransaction.objects.create(
              user=user,
              transaction_id=tran_id,
              amount=Decimal('100.00'),  # Using fixed amount from your data
              status='initiated',
              gateway_response={'payment_request': data}
          )
          print(f"Created PaymentTransaction record: {payment_transaction}")
      except Exception as db_error:
          print(f"Failed to create PaymentTransaction: {db_error}")
      
      try:
          response = requests.post(endpoint, json=data)
          response.raise_for_status()
          result = response.json()
          
          print("=== PAYMENT RESPONSE ===")
          print(json.dumps(result, indent=4))
          print("=" * 50)
          
          return JsonResponse(result)
      except requests.exceptions.RequestException as e:
          return JsonResponse({"error": f"Payment request failed: {str(e)}"}, status=500)
      except json.JSONDecodeError as e:
          return JsonResponse({"error": "Invalid response from payment gateway"}, status=500)
      except Exception as e:
          return JsonResponse({"error": str(e)}, status=500)





AAMARPAY_BASE_URL = "https://sandbox.aamarpay.com/api/v1/trxcheck/request.php"


def get_aamarpay_transaction(request_id):
    params = {
        "request_id": request_id,
        "store_id": store_id,
        "signature_key": signature_key,
        "type": "json"
    }
    r = requests.get(AAMARPAY_BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()
