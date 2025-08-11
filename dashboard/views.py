from payments.models import *
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
def create_upload_file(request):
    has_paid = PaymentTransaction.objects.filter(
        user=request.user, status='success'
    ).exists()

    if request.method == "POST":
        if not has_paid:
            messages.error(request, "You must complete payment before uploading files.")
            return redirect("create_upload_file")

        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file selected.")
            return redirect("create_upload_file")

        if not file.name.endswith((".txt", ".docx")):
            messages.error(request, "Only .txt or .docx files are allowed.")
            return redirect("create_upload_file")

        FileUpload.objects.create(
            user=request.user,
            file=file,
            filename=file.name,
            status="processing"
        )

        messages.success(request, "File uploaded successfully and is being processed.")
        return redirect("create_upload_file")

    return render(request, "dashboard/create_file_upload.html", {"has_paid": has_paid})

@login_required(login_url='login')
def uploadedfilelist(request):
    files = FileUpload.objects.filter(user=request.user).order_by('-upload_time')  # corrected order field
    return render(request, "dashboard/file_upload_list.html", {'files': files})

@login_required(login_url='login')
def activity(request):
    activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, "dashboard/activity_history.html", {'activity_logs': activity_logs})


@login_required(login_url='login')
def payment_history(request):
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, "dashboard/payment_history.html", {'payments': payments})