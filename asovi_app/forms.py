from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from allauth.account.forms import SignupForm
from .models import *


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

class IDChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['user_id']
        labels = {
            'user_id': '新しいユーザーID',
        }


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '新しいメールアドレス'

        def clean_email(self):
            """同じアドレスで仮登録段階のアカウントを消去"""
            email = self.cleaned_data['email']
            CustomUser.objects.filter(email=email, is_active=False).delete()
            try:
                EmailValidator.validate_email(email)
            except ValidationError:
                raise ValidationError('正しいメールアドレスを指定してください。')
            return email

class NotificationForm(forms.ModelForm):
   class Meta:
        model = NotificationSetting
        fields = ['good','has_saved','reply','friend']
        labels = {
           'good': "自分の投稿へのいいねを通知する",
           'has_saved': "自分の投稿が保存されたことを通知する",
           'reply': "自分の投稿への返信を通知する",
           'friend': "自分へのフレンドリクエストを通知する"
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image','body','latitude','longitude','genre']


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


class ContactForm(forms.ModelForm):
    class Meta:
        model=Contact
        fields=['content']
