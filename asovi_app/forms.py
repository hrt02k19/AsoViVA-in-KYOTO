from django import forms
from allauth.account.forms import SignupForm
from .models import CustomUser, Profile


class CustomSignupForm(SignupForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class ProfileNameForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username','icon','introduction','interested_genre','gender']
