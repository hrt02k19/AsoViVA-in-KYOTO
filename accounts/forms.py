from django import forms
from allauth.account.forms import SignupForm
from .models import CustomUser


class CustomSignupForm(SignupForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
