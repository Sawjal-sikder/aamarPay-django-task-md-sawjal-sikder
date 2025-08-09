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
# user model import User
from django.contrib.auth import get_user_model

User = get_user_model()

@csrf_exempt
@require_POST
@login_required
def create_payment(request):
      store_id = settings.AAMARPAY_STORE_ID
      signature_key = settings.AAMARPAY_SIGNATURE_KEY
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

      # print("Payment data:", json.dumps(data, indent=4))
      
      try:
          response = requests.post(endpoint, json=data)
          response.raise_for_status()
          result = response.json()
          return JsonResponse(result)
      except requests.exceptions.RequestException as e:
          return JsonResponse({"error": f"Payment request failed: {str(e)}"}, status=500)
      except json.JSONDecodeError as e:
          return JsonResponse({"error": "Invalid response from payment gateway"}, status=500)
      except Exception as e:
          return JsonResponse({"error": str(e)}, status=500)
    
    
    
def transaction_response(request):
      try:
            result = json.loads(request.body)
            tran_id = result.get("tran_id")
            store_id = result.get("store_id")
            signature_key = result.get("signature_key")
            return JsonResponse({
                  "tran_id": tran_id,
                  "store_id": store_id,
                  "signature_key": signature_key
            })
      except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)