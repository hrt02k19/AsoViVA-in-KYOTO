from django import forms
from .models import Profile,post

class ProfileNameForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username','icon','introduction','interested_genre','gender']

class PostForm(forms.ModelForm):
    class Meta:
        model=post
        fields=['image','body','latitude','longitude']