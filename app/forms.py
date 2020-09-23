from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import saleOrder, purchaseOrder


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password", ]

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username',  'password', ]

