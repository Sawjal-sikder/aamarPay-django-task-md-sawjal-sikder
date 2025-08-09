from django.shortcuts import render
from rest_framework import generics
from .serializer import UserSerializer
from django.contrib.auth.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
