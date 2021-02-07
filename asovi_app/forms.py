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
        fields = ['username','introduction']
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
    def __init__(self, *args, **kwd):
        super(PostForm, self).__init__(*args, **kwd)
        self.fields["latitude"].required = False
        self.fields["longitude"].required = False

        self.fields["latitude"].widget.attrs['placeholder'] = '地点を選択して自動入力'
        self.fields["longitude"].widget.attrs['placeholder'] = '地点を選択して自動入力'

    class Meta:
        model = Post
        fields = ['image','body','latitude','longitude','genre']
        labels = {
            'image': "写真",
            'body': "",
            'latitude': "緯度",
            'longitude': "経度",
            'genre': "投稿のジャンル"
        }


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
        (4,'半径2km以内'),
        (0,'指定なし'),
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
    nullok = forms.BooleanField(label='ジャンルなし',required=False)

class WordSearchForm(forms.Form):
    key_word = forms.CharField(label='検索:',max_length=50,required=False)


class PlaceSearchForm(forms.Form):
    types = [
        ('none', '指定しない'),
        ('amusement_park', '遊園地'),
        ('aquarium', '水族館'),
        ('art_gallery', '美術館'),
        ('bar', 'バー'),
        ('bowling_alley', 'ボーリング場'),
        ('cafe', 'カフェ'),
        ('campground', 'キャンプ場'),
        ('lodging', '宿泊施設'),
        ('movie_theater', '映画館'),
        ('museum', '博物館'),
        ('park', '公園'),
        ('restaurant', 'レストラン'),
        ('shopping_mall', 'ショッピングセンター'),
        ('spa', '温泉'),
        ('stadium', 'スタジアム'),
        ('store', '店'),
        ('tourist_attraction', '観光名所'),
        ('zoo', '動物園'),
    ]
    radius = forms.IntegerField(label='検索対象の半径', max_value=50000, min_value=0, initial=1000)
    keyword = forms.CharField(label='キーワード', max_length=200, required=False, initial='')
    place_type = forms.MultipleChoiceField(label='カテゴリー', required=False, choices=types, widget=forms.RadioSelect())
    lat = forms.FloatField(label='緯度', required=False, initial=34.987)
    lng = forms.FloatField(label='経度', required=False, initial=135.759)


class ContactForm(forms.ModelForm):
    class Meta:
        model=Contact
        fields=['content']


class SignOutForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'メールアドレス',
    }))
    password = forms.CharField(max_length=200, required=True, widget=forms.PasswordInput(attrs={
        'placeholder': 'パスワード',
    }))
