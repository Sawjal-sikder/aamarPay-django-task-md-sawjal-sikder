from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'main.html')

def payment_history(request):
    return render(request, "dashboard/payment_history.html")