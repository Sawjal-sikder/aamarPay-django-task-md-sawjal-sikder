from django.urls import path
from .views import *

urlpatterns = [
    path('home/', home, name='dashboard'),
    path('login/', LoginView, name='LoginView'),
    path('logout/', LogoutView, name='LogoutView'),
    path("create_upload_file/",create_upload_file, name="create_upload_file"),
    path("uploadedfilelist/",uploadedfilelist, name="uploadedfilelist"),
    path("activity/",activity, name="activity"),
    path("transition/",payment_history, name="transition")
]
