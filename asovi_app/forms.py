from django import forms

from allauth.account.forms import SignupForm
from .models import CustomUser, Profile, Post, Good


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
        labels = {
            'username': "名前", 
        }

class PostForm(forms.ModelForm):
    class Meta:
        model=post
        fields=['image','body','latitude','longitude','user','genre']                                                                                                                                                                     


class GoodForm(forms.ModelForm):
    class Meta:
        model=Good
        fields=['good']

class SaveForm(forms.Form):
    save=forms.BooleanField(label='Checkbox',required=False)
    model=Post
    fields=['image','body','latitude','longitude']

class FindForm(forms.Form):
    find = forms.CharField(max_length=100, required=False)

class LocationSearchForm(forms.Form):
    radius = [
        (1,'半径200m以内'),
        (2,'半径500m以内'),
        (3,'半径1km以内'),
        (4,'半径2km以内')
    ]
    choice = forms.ChoiceField(label='検索の範囲を指定', choices=radius, widget=forms.RadioSelect(), required=False)

class GenreSearchForm(forms.Form):
    food = forms.BooleanField(label='食事',required=False)
    music = forms.BooleanField(label='音楽',required=False)
    nature = forms.BooleanField(label='自然',required=False)
    art = forms.BooleanField(label='芸術',required=False)
    temple = forms.BooleanField(label='寺社',required=False)
    shopping = forms.BooleanField(label='買物',required=False)
    indoor = forms.BooleanField(label='屋内',required=False)
    outdoor = forms.BooleanField(label='屋外',required=False)
    exercise = forms.BooleanField(label='運動',required=False)

class WordSearchForm(forms.Form):
    key_word = forms.CharField(label='検索:',max_length=50,required=False)
