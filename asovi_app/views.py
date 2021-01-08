from typing import Counter
from django.core import serializers
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.db import IntegrityError
from django.db.models import Subquery, OuterRef
from django.db.models.query import EmptyQuerySet
from django.db.models.query_utils import Q
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from allauth.exceptions import ImmediateHttpResponse
from allauth.account import app_settings
from allauth.account.views import SignupView
from allauth.account.utils import complete_signup

from .forms import CustomSignupForm, GenreSearchForm, LocationSearchForm, ProfileForm, PostForm, FindForm, WordSearchForm, GoodForm, SaveForm,ContactForm,EmailChangeForm,IDChangeForm, NotificationForm, SignOutForm
from .models import *

from asoviva.local_settings import API_KEY

import datetime, random, string, googlemaps, sys

sys.path.append('../asoviva')
#from asoviva.local_settings import API_KEY

class MySignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        self.user = form.save(self.request)
        self.user.user_id = CustomUserManager.generate_user_id(self, 10)
        self.user.save()
        try:
            return complete_signup(
                self.request,
                self.user,
                app_settings.EMAIL_VERIFICATION,
                # self.get_success_url(),
                success_url='asovi_app:profile_edit',
            )
        except ImmediateHttpResponse as e:
            return e.response

def count_new_events(user: CustomUser):
    setting = user.user_notification
    events_num = 0
    if setting.good :
        new_good = Good.objects.filter(article__posted_by=user, checked=False)
        events_num += new_good.count()
    if setting.has_saved :
        new_save = Save.objects.filter(item__posted_by=user, checked=False)
        events_num += new_save.count()
    if setting.reply :
        new_reply = Reply.objects.filter(post__posted_by=user, checked=False)
        events_num += new_reply.count()
    if setting.friend :
        new_friend_request = Friend.objects.filter(requestee=user, friended=False, request_checked=False)
        events_num += new_friend_request.count()

    return events_num

def generate_genre_list(profile: Profile):
    list = []
    qs = profile.interested_genre.all()
    for genre in qs:
        list.append(genre.pk)
    #print(st)
    return list

def profile_edit(request):
    params = {}
    # obj_exists = True
    try:
        obj = Profile.objects.get(user=request.user)
    except:
        obj = Profile.objects.create(user=request.user)
    params['form'] = ProfileForm(instance=obj)
    params['icon'] = obj.icon
    params['genre_list']=generate_genre_list(obj)
    # print(generate_genre_list(obj))
    # obj = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        profile = ProfileForm(request.POST, instance=obj)
        profile.save()
        if 'icon' in request.FILES:
            obj.icon = request.FILES['icon']
            obj.save()
        if "1" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=1))
        if "2" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=2))
        if "3" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=3))
        if "4" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=4))
        if "5" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=5))
        if "6" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=6))
        if "7" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=7))
        if "8" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=8))
        if "9" in request.POST:
            obj.interested_genre.add(Genre.objects.get(pk=9))
        params['form']=ProfileForm(instance=obj)
        params['icon']=obj.icon
        params['genre_list']=generate_genre_list(obj)
        return redirect('/my_page/')
    return render(request, 'asovi_app/profile_edit.html', params)


def post_view(request):

    params={
        'form':PostForm(),
    }
    if request.method=='POST':
        form = PostForm(request.POST)
        gmaps = googlemaps.Client(key=API_KEY)
        # print('送信しました')
        user = request.user
        genre = None
        if request.POST['genre'] == '1':
            genre=Genre.objects.get(pk=1)
        elif request.POST['genre'] == '2':
            genre=Genre.objects.get(pk=2)
        elif request.POST['genre'] == '3':
            genre=Genre.objects.get(pk=3)
        elif request.POST['genre'] == '4':
            genre=Genre.objects.get(pk=4)
        elif request.POST['genre'] == '5':
            genre=Genre.objects.get(pk=5)
        elif request.POST['genre'] == '6':
            genre=Genre.objects.get(pk=6)
        elif request.POST['genre'] == '7':
            genre=Genre.objects.get(pk=7)
        elif request.POST['genre'] == '8':
            genre=Genre.objects.get(pk=8)
        elif request.POST['genre'] == '9':
            genre=Genre.objects.get(pk=9)
        # now=datetime.datetime.now()
        image = request.FILES['image']
        body = request.POST['body']
        lat= request.POST['latitude']
        lng= request.POST['longitude']

        place = gmaps.reverse_geocode((lat, lng))
        #print(place)
        place_id = place[0]['place_id']
        print(place_id)

        new_post = Post(posted_by=user,image=image,genre=genre,body=body,latitude=lat,longitude=lng,place_id=place_id)
        new_post.save()
        print('保存されました')
        return redirect('/post_completed/' + str(new_post.pk))  #投稿後に遷移するページが完成次第post/から変更する

    return render(request,'asovi_app/post.html',params)

def post_completed(request,pk):
    return render(request, 'asovi_app/post_completed.html', {'post_pk': pk})



def look(request,id,user):
    data=Good.objects.filter(article=id,user=user)
    post_data=Post.objects.filter(id=id)
    save_data=Save.objects.filter(item=id,person=user)
    if request.method=='POST':
        form=GoodForm(request.POST)
        form.save()
        form2=SaveForm(request.POST)
        if form.good==False:
            if data.good==True:
                post_data.like+=1
                post_data.save()

        else:
            if data.good==False:
                post_data.like-=1
                post_data.save()

        if save_data.exists():
            if form2.save==False:
                save_data.delete()
        else:
            if form2.save==True:
                save_data=Save(item=id,person=user)
                save_data.save()


    else:
        if data.good==True:
            form=GoodForm(initial={'good':True})
        else:
            form=GoodForm(initial={'good':False})

        if save_data.exists():
            form2=SaveForm(initial={'save':True})
        else:
            form2=SaveForm(initial={'save':False})

    params={'form':form,
            'form2':form2,
            'post_data':post_data,

    }

    return render(request,'asovi_app/look.html',params)

def post_detail(request,pk):
    post = Post.objects.get(pk=pk)
    replies = post.post_reply.all().order_by("-pub_date")
    params = {
        'post': post,
        'replies': replies
    }
    return render(request,'asovi_app/post_detail.html',params)



def friend_request(request, pk):
    params = {}
    if request.method == 'POST':
        requestor=CustomUser.objects.get(pk=request.user.pk)
        requestee=CustomUser.objects.get(pk=pk)
        new_request = Friend(
            requestor=requestor,
            requestee=requestee,
        )
        new_request.save()

        params = {
            'requestor': requestor,
            'requestee': requestee,
        }
    return render(request, 'asovi_app/friend_request.html', params)

def friend_request_accept(request):
    params = {}
    if request.method == 'GET':
        query = request.GET.get('search_id')
        if query:
            new_requests = Friend.objects.filter(
                requestee=request.user, friended=False, requestor__user_id__icontains=query
                ).annotate(
                requestor_username = Subquery(
                    Profile.objects.filter(user=OuterRef("requestor")).values('username')
                ),
                requestor_icon=Subquery(
                    Profile.objects.filter(user=OuterRef("requestor")).values('icon')
                ),
                )
            if not new_requests:
                params["no_results"] = '検索された文字列にマッチするユーザーは見つかりませんでした。'

        else:
            new_requests = Friend.objects.filter(
                friended=False, requestee=request.user
                ).annotate(
                requestor_username = Subquery(
                    Profile.objects.filter(user=OuterRef("requestor")).values('username')
                ),
                requestor_icon=Subquery(
                    Profile.objects.filter(user=OuterRef("requestor")).values('icon')
                ),
            )
            print(new_requests)
            if not new_requests:
                params["no_results"] = '現在、あなたへの友達申請はありません。'
        params["new_requests"] = new_requests

    if request.method == 'POST':
        new_request_pk = request.POST['friend_request_pk']
        new_request = Friend.objects.get(pk=new_request_pk)
        if 'accept' in request.POST:
            new_request.friended = True
            new_request.friended_date = datetime.datetime.now()
            new_request.save()

        elif 'reject' in request.POST:
            new_request.delete()

    return render(request, 'asovi_app/friend_request_accept.html', params)


def friend_block(request,pk):
    print(request.POST)
    me = request.user
    blocked_friend = CustomUser.objects.get(pk=pk)
    block = Block(blocker=me,blocked=blocked_friend)
    block.save()
    friend = Friend.objects.get(Q(requestor=me,requestee=blocked_friend)|Q(requestor=blocked_friend,requestee=me))
    friend.delete()
    return redirect('asovi_app:friend_list')

def friend_list(request,*args):
    me = request.user
    my_friend = Friend.objects.filter( Q(requestor=me) | Q(requestee=me)).filter(friended=True).annotate(
        requestor_username=Subquery(
            Profile.objects.filter(user=OuterRef("requestor")).values("username")
        ),
        requestor_icon=Subquery(
            Profile.objects.filter(user=OuterRef("requestor")).values("icon")
        ),
        requestee_username=Subquery(
            Profile.objects.filter(user=OuterRef("requestee")).values("username")
        ),
        requestee_icon=Subquery(
            Profile.objects.filter(user=OuterRef("requestee")).values("icon")
        ),
    ).order_by("-friended_date")
    my_friend_requesting = Friend.objects.filter(requestor=me,friended=False).annotate(
        requestee_username=Subquery(
            Profile.objects.filter(user=OuterRef("requestee")).values("username")
        ),
        requestee_icon=Subquery(
            Profile.objects.filter(user=OuterRef("requestee")).values("icon")
        )
    ).order_by("-requested_date")
    my_friend_requested = Friend.objects.filter(requestee=me,friended=False).annotate(
        requestor_icon=Subquery(
            Profile.objects.filter(user=OuterRef("requestor")).values("icon")
        )
    ).order_by("-requested_date")
    my_friend_requested_num = len(my_friend_requested)
    if my_friend_requested_num > 0:
        my_friend_requested_top = my_friend_requested[0]
    else:
        my_friend_requested_top = None

    params = {
        'me': me,
        'friend': my_friend,
        'my_friend_requesting': my_friend_requesting,
        'my_friend_requesting_num': len(my_friend_requesting),
        'my_friend_requested_top': my_friend_requested_top,
        'my_friend_requested_num': my_friend_requested_num
    }
    return render(request, 'asovi_app/friend_list.html', params)

def post_map(request):
    user = request.user
    involved_blocks = Block.objects.filter( Q(blocker=user) | Q(blocked=user) )
    blocked_users = []
    for block_obj in involved_blocks:
        if block_obj.blocker == user:
            blocked_users.append(block_obj.blocked)
        else:
            blocked_users.append(block_obj.blocker)
    posts = Post.objects.all().exclude(posted_by__in=blocked_users)
    loc_form = LocationSearchForm()
    genre_form = GenreSearchForm()
    word_form = WordSearchForm()
    radius = 0
    if request.method == 'POST':
        if 'location_search' in request.POST :
            loc_form = LocationSearchForm(request.POST)
            radius = request.POST.get('choice')
            print(radius)
        elif 'genre_search' in request.POST :
            genre_form = GenreSearchForm(request.POST)
            selected_genre = []
            if 'food' in request.POST :
                selected_genre.append(Genre.objects.get(pk=1))
            if 'music' in request.POST :
                selected_genre.append(Genre.objects.get(pk=2))
            if 'nature' in request.POST :
                selected_genre.append(Genre.objects.get(pk=3))
            if 'art' in request.POST :
                selected_genre.append(Genre.objects.get(pk=4))
            if 'temple' in request.POST :
                selected_genre.append(Genre.objects.get(pk=5))
            if 'shopping' in request.POST :
                selected_genre.append(Genre.objects.get(pk=6))
            if 'indoor' in request.POST :
                selected_genre.append(Genre.objects.get(pk=7))
            if 'outdoor' in request.POST :
                selected_genre.append(Genre.objects.get(pk=8))
            if 'exercise' in request.POST :
                selected_genre.append(Genre.objects.get(pk=9))
            posts = posts.filter(genre__in=selected_genre)
        elif 'word_search' in request.POST :
            word_form = WordSearchForm(request.POST)
            kw = request.POST.get('key_word')
            posts = posts.filter(body__contains=kw)

    posts_json = serializers.serialize('json',posts)
    genre_json = serializers.serialize('json',Genre.objects.all().order_by('pk'))

    params = {
        'posts': posts,
        'posts_json': posts_json,
        'genre_json': genre_json,
        'loc_form': loc_form,
        'genre_form': genre_form,
        'word_form': word_form,
        'radius': radius
    }
    return render(request,'asovi_app/post_map.html', params)


def place_detail(request, place_id):
    user = request.user
    # 詳細情報取得
    # APIキーはlocal_settings.pyに設定しておく
    map_api = googlemaps.Client(API_KEY)
    # 取得したい情報を設定
    fields = ['name', 'address_component', 'business_status', 'geometry']
    place = map_api.place(place_id=place_id, fields=fields, language='ja')
    details = place['result']
    business_status = details['business_status']
    if business_status == 'CLOSED_TEMPORARILY':
        business_status = '一時休業中'
    elif business_status == 'CLOSED_PERMANENTLY':
        business_status = '閉鎖中'
    else:
        business_status = ''
    location = place['result']['geometry']['location']
    address_components = place['result']['address_components']
    address = '〒'
    for address_component in reversed(address_components):
        if address_component['types'] == ["country", "political"]:
            continue
        else:
            address += address_component['long_name']

    # 投稿取得
    involved_blocks = Block.objects.filter( Q(blocker=user) | Q(blocked=user) )
    blocked_users = []
    for block_obj in involved_blocks:
        if block_obj.blocker == user:
            blocked_users.append(block_obj.blocked)
        else:
            blocked_users.append(block_obj.blocker)

    post_list = Post.objects.filter(place_id=place_id).exclude(posted_by__in=blocked_users)

    params = {
        'details': details,
        'business_status': business_status,
        'location': location,
        'address': address,
        'post_list': post_list,
        'API_KEY': API_KEY,
    }
    return render(request, 'asovi_app/place_detail.html', params)


class FindUserView(generic.ListView):
    template_name = 'asovi_app/find_user.html'
    paginate_by = 10
    model = CustomUser

    def get_queryset(self):
        query = self.request.GET.get('search_id')

        if query:
            object_list = CustomUser.objects.filter(user_id__icontains=query)
        else:
            object_list = []
        return object_list


def user_profile(request, pk):
    me = CustomUser.objects.get(pk=request.user.pk)
    user = CustomUser.objects.get(pk=pk)
    params = {}
    try:
        profile = Profile.objects.get(user=user)
        interested_genres = profile.interested_genre.all()
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=user)
        interested_genres = profile.interested_genre.all()
    post_list = Post.objects.filter(posted_by=user).order_by("-time")
    friend_num = Friend.objects.filter(Q(requestor=user)|Q(requestee=user)).filter(friended=True).count()
    post_num = Post.objects.filter(posted_by=user).count()

    post_list_json = serializers.serialize('json', post_list)

    params = {
        'me': me,
        'user': user,
        'profile': profile,
        'interested_genres': interested_genres,
        'post_list': post_list,
        'friend_num': friend_num,
        'post_num': post_num,
        'post_list_json': post_list_json,
    }
    return render(request, 'asovi_app/user_profile.html', params)


def post_list(request, pk):
    user = CustomUser.objects.get(pk=pk)
    post_list = Post.objects.filter(posted_by=user).order_by("-time")
    post_list_json = serializers.serialize('json', post_list)
    params = {
        'post_list': post_list,
        'post_list_json': post_list_json,
    }
    return render(request, 'asovi_app/post_list.html', params)


def my_page(request):
    me = request.user
    friend_num = Friend.objects.filter(Q(requestor=me)|Q(requestee=me)).filter(friended=True).count()
    params = {
        'me': me,
        'notification': count_new_events(me),
        'friend_num': friend_num,
    }
    return render(request, 'asovi_app/mypage.html', params)


def change_id(request):
    me = CustomUser.objects.get(email=request.user)
    form = IDChangeForm
    params = {'form': form}

    if request.method == 'POST':
        form = IDChangeForm(request.POST)
        try:
            me.user_id = request.POST['user_id']
            me.save()
            return redirect(to='asovi_app:change_id_completed')

        except IntegrityError:
            msg = '他のユーザーがこのIDを使用しています。'
            params['msg'] = msg
        else:
            msg = 'ユーザーIDの変更に失敗しました。'
            params['msg'] = msg

    return render(request, 'asovi_app/change_id.html', params)


def change_id_completed(request):
    params = {
        'change_what': 'ユーザーID',
        'user': request.user,
    }
    return render(request, 'asovi_app/change_completed.html', params)


def check_event(request):
    user = request.user
    setting = user.user_notification
    now = datetime.datetime.now()
    expire_limit_time = now - datetime.timedelta(hours=24)
    new_good = Good.objects.none()
    new_save = Save.objects.none()
    new_reply = Reply.objects.none()
    new_friend_request = Friend.objects.none()
    if setting.good :
        new_good = Good.objects.filter(article__posted_by=user, pub_date__gte=expire_limit_time).annotate(
            user_username = Subquery(
                Profile.objects.filter(user=OuterRef("user")).values('username')
            ),
            user_icon = Subquery(
                Profile.objects.filter(user=OuterRef("user")).values('icon')
            )
        )

    if setting.has_saved :
        new_save = Save.objects.filter(item__posted_by=user, pub_date__gte=expire_limit_time).annotate(
            saver_username = Subquery(
                Profile.objects.filter(user=OuterRef("person")).values('username')
            )
        )
    if setting.reply :
        new_reply = Reply.objects.filter(post__posted_by=user, pub_date__gte=expire_limit_time).annotate(
            replier_username = Subquery(
                Profile.objects.filter(user=OuterRef("posted_by")).values('username')
            )
        )
    if setting.friend :
        new_friend_request = Friend.objects.filter(requestee=user, friended=False, requested_date__gte=expire_limit_time).annotate(
            requestor_username = Subquery(
                Profile.objects.filter(user=OuterRef("requestor")).values('username')
            ),
            requestor_icon=Subquery(
                Profile.objects.filter(user=OuterRef("requestor")).values('icon')
            ),
        )

    Good.objects.filter(article__posted_by=user).update(checked=True)
    Save.objects.filter(item__posted_by=user).update(checked=True)
    Reply.objects.filter(post__posted_by=user).update(checked=True)
    Friend.objects.filter(requestee=user).update(request_checked=True)


    params = {
        'new_good_num': new_good.count(),
        'new_save_num': new_save.count(),
        'new_reply_num': new_reply.count(),
        'new_friend_request_num': new_friend_request.count(),
        'new_goods': new_good,
        'new_saves': new_save,
        'new_replies': new_reply,
        'new_friend_requests': new_friend_request,
    }

    return render(request, 'asovi_app/check_event.html', params)

def notification_setting(request):
    try:
        obj = get_object_or_404(NotificationSetting,user=request.user)
    except:
        obj = NotificationSetting.objects.create(user=request.user)
    form = NotificationForm(instance=obj)
    if request.method == 'POST':
        form = NotificationForm(request.POST,instance=obj)
        form.save()

    return render(request, 'asovi_app/notification_setting.html', {'form': form})

def change_id(request):
    me = CustomUser.objects.get(email=request.user)
    form = IDChangeForm
    params = {'form': form}

    if request.method == 'POST':
        form = IDChangeForm(request.POST)
        try:
            me.user_id = request.POST['user_id']
            me.save()
            return redirect(to='asovi_app:change_id_completed')

        except IntegrityError:
            msg = '他のユーザーがこのIDを使用しています。'
            params['msg'] = msg
        else:
            msg = 'ユーザーIDの変更に失敗しました。'
            params['msg'] = msg

    return render(request, 'asovi_app/change_id.html', params)

def change_id_completed(request):
    params = {
        'change_what': 'ユーザーID',
    }
    return render(request, 'asovi_app/change_completed.html', params)

class EmailChange(LoginRequiredMixin, generic.FormView):
    template_name = 'asovi_app/change_email.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        """認証用メールの発行"""
        user = self.request.user
        email = form.cleaned_data['email']

        current_site = get_current_site(self.request)
        # domain = current_site.domain
        domain = 'localhost:8000'
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(email),
            'user': user,
        }
        subject = render_to_string('account/email/email_confirmation_subject.txt', context).strip()
        message = render_to_string('account/email/email_change_confirmation_message.txt', context)
        send_mail(subject, message, 'asoviva@in.kyoto', [email])
        # user.email_user(subject, message)

        return redirect('asovi_app:change_email_sent')

def change_email_sent(request):
    params = {
        'user': request.user,
    }
    return render(request, 'asovi_app/change_email_sent.html')


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """変更"""
    template_name = 'asovi_app/change_completed.html'
    timeout_seconds = 60 * 60 * 24  # リンクの有効期限は１日
    extra_context = {'change_what': 'メールアドレス'}

    def get(self, request, **kwargs):
        """tokenが正しければ本登録"""
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            CustomUser.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)

def logout_completed(request):
    return render(request, 'asovi_app/logout_completed.html')

def signout(request):
    form = SignOutForm()
    params = {'form': form}
    if request.method == 'POST':
        form = SignOutForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        if request.user.email == email and check_password(password, request.user.password):
            """メールもパスワードもログインユーザーのものと同じならアカウント削除"""
            me = CustomUser.objects.get(email=request.user)
            me.delete()
            return redirect(to='asovi_app:signout_completed')
        elif request.user.email != email:
            params['msg'] = 'メールアドレスが違います。'
        elif request.user.password != password:
            params['msg'] = 'パスワードが違います。'
        else:
            params['msg'] = 'アカウントを削除できませんでした。'
    return render(request, 'asovi_app/signout.html', params)


def signout_completed(request):
    return render(request, 'asovi_app/signout_completed.html')


def contact(request):
    who=request.user
    if request.method=='POST':
        form=ContactForm(request.POST)
        if form.is_valid():
            content=form.cleaned_data('content')
            contact=Contact(contacter=who,content=content)
            contact.save()
            return redirect(to='asovi_app:contact_fin')


    else:
        form=ContactForm()
        params={
            'form':form
        }
        return render(request,'asovi_app/contact.html',params)


def contact_fin(request):
    params={
        'page':'asovi_app:contact_fin',
    }

    return render(request,'asovi_app/contact_fin.html',params)

def save_article(request):
    person=request.user
    data=Save.objects.filter(person=person)
    params={
        'data':data,
    }
    return render(request,'asovi_app/save_article.html',params)


def settings(request):
    return render(request, 'asovi_app/settings.html')
