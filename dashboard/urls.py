from django.urls import path
from .views import *

urlpatterns = [
    path('home/', home, name='dashboard'),
    path('login/', LoginView, name='LoginView'),
    path('logout/', LogoutView, name='LogoutView'),
    path("uploadedfilelist/",uploadedfilelist, name="uploadedfilelist"),
    path("activity/",activity, name="activity"),
    path("transition/",payment_history, name="transition")
]
