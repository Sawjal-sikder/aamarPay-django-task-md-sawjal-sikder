from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # or any page you want after login
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "admin/login.html")

def LogoutView(request):
    logout(request)
    return redirect("LoginView")

@login_required(login_url='login')
def home(request):
    return render(request, 'main.html')
@login_required(login_url='login')
def payment_history(request):
    return render(request, "dashboard/payment_history.html")