from typing import Counter
from django.core import serializers
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.db import IntegrityError
from django.db.models import Subquery, OuterRef, Count
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

from .forms import CustomSignupForm, GenreSearchForm, LocationSearchForm, ProfileForm, PostForm, FindForm, WordSearchForm, GoodForm, SaveForm,ContactForm,EmailChangeForm,IDChangeForm, NotificationForm, SignOutForm, PlaceSearchForm
from .models import *


import datetime, json, random, string, googlemaps, sys
sys.path.append('../asoviva')
from asoviva.local_settings import API_KEY

class MySignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        self.user = form.save(self.request)
        self.user.user_id = CustomUserManager.generate_user_id(self, 10)
        self.user.save()
        NotificationSetting.objects.create(
            user=self.user,
            good=True,
            has_saved=True,
            reply=True,
            friend=True,
        )
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
    try:
        setting = user.user_notification
    except ObjectDoesNotExist:
        setting = NotificationSetting.objects.create(
            user=user,
            good=True,
            has_saved=True,
            reply=True,
            friend=True,
        )

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
        #print(request.POST)
        #print(request.FILES)
        profile = ProfileForm(request.POST, instance=obj)
        if profile.is_valid():
            profile.save()
        if 'icon' in request.FILES:
            obj.icon = request.FILES['icon']
            obj.save()
        obj.interested_genre.clear()
        int_genre_list = request.POST.getlist('interested_genre')
        if "1" in int_genre_list:
            print('yes')
            obj.interested_genre.add(Genre.objects.get(pk=1))
        if "2" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=2))
        if "3" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=3))
        if "4" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=4))
        if "5" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=5))
        if "6" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=6))
        if "7" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=7))
        if "8" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=8))
        if "9" in int_genre_list:
            obj.interested_genre.add(Genre.objects.get(pk=9))
        params['form']=ProfileForm(instance=obj)
        params['icon']=obj.icon
        params['genre_list']=generate_genre_list(obj)
        return redirect('/post_list/' + str(request.user.pk))
    return render(request, 'asovi_app/profile_edit.html', params)


def post_view(request):
    request.session.set_expiry(0)  # ブラウザを閉じたらセッションを破棄
    params = {}
    # 地点変更せず戻って来た時に入力途中のフォームを表示
    params['form'] = PostForm(request.session.get('post_form_data'))
    if request.method == 'POST':
        if 'change_place' in request.POST:
            # 入力したデータをセッションに保存して地点変更ページへ
            request.session['post_form_data'] = request.POST
            return redirect('asovi_app:change_place')

        elif 'decide_place' in request.POST:
            # 地点変更して戻ってきたとき
            request.session.get('post_form_data')['latitude'] = request.POST.get('place_lat')
            request.session.get('post_form_data')['longitude'] = request.POST.get('place_lng')
            params['form'] = PostForm(request.session.get('post_form_data'))
            params['place_lat'] = request.POST.get('place_lat')
            params['place_lng'] = request.POST.get('place_lng')
            params['place_name'] = request.POST.get('place_name')
            # print(params['place_lat'])
            # print(params['place_lng'])

        else:
            # 投稿ボタンを押したとき
            params['form'] = PostForm(request.POST)
            gmaps = googlemaps.Client(key=API_KEY)
            user = request.user
            genre = None
            if request.POST.get('interested_genre') == '1':
                genre=Genre.objects.get(pk=1)
            elif request.POST.get('interested_genre') == '2':
                genre=Genre.objects.get(pk=2)
            elif request.POST.get('interested_genre') == '3':
                genre=Genre.objects.get(pk=3)
            elif request.POST.get('interested_genre') == '4':
                genre=Genre.objects.get(pk=4)
            elif request.POST.get('interested_genre') == '5':
                genre=Genre.objects.get(pk=5)
            elif request.POST.get('interested_genre') == '6':
                genre=Genre.objects.get(pk=6)
            elif request.POST.get('interested_genre') == '7':
                genre=Genre.objects.get(pk=7)
            elif request.POST.get('interested_genre') == '8':
                genre=Genre.objects.get(pk=8)
            elif request.POST.get('interested_genre') == '9':
                genre=Genre.objects.get(pk=9)
            if request.FILES:
                image = request.FILES['image']
            else:
                image = ''
            body = request.POST['body']
            lat= request.POST.get('latitude')
            lng = request.POST.get('longitude')
            place = gmaps.reverse_geocode((lat, lng), language='ja')
            place_id = place[0]['place_id']
            #ユーザーが現在地ボタンを押さなかった時の挙動をどうするのか?
            new_post = Post(posted_by=user,image=image,genre=genre,body=body,latitude=lat,longitude=lng,place_id=place_id)
            new_post.save()
            return redirect('/post_completed/' + str(new_post.pk))  #投稿後に遷移するページが完成次第post/から変更する

    return render(request,'asovi_app/post.html',params)

def post_completed(request,pk):
    return render(request, 'asovi_app/post_completed.html', {'post_pk': pk,'user':request.user})


def change_place(request):
    params = {
        #'search_form': PlaceSearchForm(),
        'post_form': PostForm()
    }

    # if request.method == 'POST':
    #     search_form = PlaceSearchForm(request.POST)
    #     keyword = request.POST['keyword']
    #     radius = request.POST['radius']
    #     place_type = request.POST['place_type']
    #     lat = request.POST.get('place_lat')
    #     lng = request.POST.get('place_lng')

    #     gmaps = googlemaps.Client(API_KEY)

    #     if lat == None or lng == None:
    #         search_results = gmaps.places_nearby(location={'lat': 34.987, 'lng': 135.759}, radius=radius, keyword=keyword, type=place_type, language='ja')

    #     else:
    #         search_results = gmaps.places_nearby(location={'lat': lat, 'lng': lng}, radius=radius, keyword=keyword, type=place_type, language='ja')

    #     results = search_results['results']
    #     results_json = json.dumps(results)
    #     params = {
    #         'search_form': search_form,
    #         'results': results,
    #         'results_json': results_json,
    #     }
    return render(request, 'asovi_app/change_place.html', params)



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

def post_delete(request,pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return render(request,'asovi_app/post_delete.html',{'user':request.user})

def friend_request(request, pk):
    params = {}
    if request.method == 'POST':
        requestor=CustomUser.objects.get(pk=request.user.pk)
        requestee=CustomUser.objects.get(pk=pk)
        already_friend = Friend.objects.filter(Q(requestor=requestor,requestee=requestee)|Q(requestor=requestee,requestee=requestor))
        if len(already_friend) > 0 :
            pass
        else:
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
    if request.method == 'POST':
        new_request_pk = request.POST['friend_request_pk']
        new_request = Friend.objects.get(pk=new_request_pk)
        if 'accept' in request.POST:
            new_request.friended = True
            new_request.friended_date = datetime.datetime.now()
            new_request.save()
        elif 'reject' in request.POST:
            new_request.delete()
    else:
        query = request.GET.get('search_id')
        if query is not None:
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
            params["new_requests"] = new_requests
            return render(request, 'asovi_app/friend_request_accept.html', params)
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
    return render(request, 'asovi_app/friend_request_accept.html', params)


def friend_block(request,pk):
    me = request.user
    print(pk)
    blocked_friend = CustomUser.objects.get(pk=pk)
    block = Block(blocker=me,blocked=blocked_friend)
    block.save()
    friend = Friend.objects.get(Q(requestor=me,requestee=blocked_friend)|Q(requestor=blocked_friend,requestee=me))
    friend.delete()
    return redirect('/friend_list/')

def friend_list(request,*args):
    me = request.user
    if request.method == 'POST':
        selected_pk = request.POST['friend_pk']
        selected_user = CustomUser.objects.get(pk=selected_pk)
        selected_friend = Friend.objects.get(Q(requestor=me,requestee=selected_user)|Q(requestor=selected_user,requestee=me))
        selected_friend.delete()
        return redirect('/friend_list/')
    params = {}
    query = request.GET.get('search_id')
    if query is not None:
        my_friend = Friend.objects.filter( Q(requestor=me,requestee__user_id__icontains=query) | Q(requestee=me,requestor__user_id__icontains=query)).filter(friended=True).annotate(
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
        my_friend_requesting = Friend.objects.filter(requestor=me,requestee__user_id__icontains=query,friended=False).annotate(
            requestee_username=Subquery(
            Profile.objects.filter(user=OuterRef("requestee")).values("username")
            ),
            requestee_icon=Subquery(
                Profile.objects.filter(user=OuterRef("requestee")).values("icon")
            )
        ).order_by("-requested_date")
        my_friend_requested = Friend.objects.filter(requestee=me, friended=False).annotate(
            requestor_icon=Subquery(
            Profile.objects.filter(user=OuterRef("requestor")).values("icon")
            )
        ).order_by("-requested_date")
        my_friend_requested_num = len(my_friend_requested)
        if my_friend_requested_num > 0:
            my_friend_requested_top = my_friend_requested[0]
        else:
            my_friend_requested_top = None
    else:
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


def place_search(request):
    me = request.user
    if request.method == 'GET':
        posts = Post.objects.all()
        posts_json = serializers.serialize('json', posts)

        good_data = Post.objects.annotate(
            liked = Subquery(
                Good.objects.filter(
                    user=me, article=OuterRef('pk'), good=True
                    ).values('good').annotate(count=Count('pk')).values('count')
                ),
        )
        good_data_json = serializers.serialize('json', good_data)
        liked_list = []  # いいねした投稿のリスト
        for data in good_data:
            if data.liked != None:
                # いいねしてある場合
                liked_list.append(data)

        liked_list_json = serializers.serialize('json', liked_list)
        params = {
            'me': me,
            'form': PlaceSearchForm,
            'posts_json': posts_json,
            'posts': posts,
            'liked_list_json': liked_list_json,
        }

    if request.method == 'POST':
        if "good_button" in request.POST:
            """いいねボタンの場合の処理"""
            gooded_post = Post.objects.get(pk=request.POST['post_pk'])
            Good.objects.filter(user=me).filter(article=gooded_post)

            if 'good' in request.POST:
                """いいねしたとき"""
                new_good = Good(
                    user=me,
                    good=True,
                    article=gooded_post
                )
                new_good.save()
                gooded_post.like += 1
                gooded_post.save()

            else:
                """いいね解除したとき"""
                stop_good = Good.objects.filter(user=me).filter(article=gooded_post).latest('pub_date')
                stop_good.delete()
                gooded_post.like -= 1
                gooded_post.save()
            return redirect('asovi_app:place_search')


        else:
            """検索の場合の処理"""
            form = PlaceSearchForm(request.POST)
            keyword = request.POST.get('keyword')
            radius = request.POST.get('radius')
            place_type = request.POST.get('place_type')
            lat = request.POST.get('lat')
            lng = request.POST.get('lng')

            gmaps = googlemaps.Client(API_KEY)

            if lat == None or lng == None:
                search_results = gmaps.places_nearby(location={'lat': 34.987, 'lng': 135.759}, radius=radius, keyword=keyword, type=place_type, language='ja')

            else:
                search_results = gmaps.places_nearby(location={'lat': lat, 'lng': lng}, radius=radius, keyword=keyword, type=place_type, language='ja')

            results = search_results['results']
            posts = Post.objects.filter(place_id__in=[result.get('place_id') for result in results])

            posts_json = serializers.serialize('json', posts)
            results_json = json.dumps(results)
            params = {
                'me': request.user,
                'form': form,
                'results': results,
                'results_json': results_json,
                'posts_json': posts_json,
            }

    return render(request, 'asovi_app/place_search.html', params)

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
        print(query)
        if query:
            object_list = CustomUser.objects.filter(user_id__icontains=query)
        else:
            object_list = []
        print(object_list)
        return object_list
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        me = self.request.user
        friend_qs = Friend.objects.filter(Q(requestor=me)|Q(requestee=me))
        friend = friend_qs.filter(friended=True)
        friend_request = friend_qs.filter(friended=False)
        friend_list = []
        friend_request_list = []
        for relation in friend:
            if relation.requestor == me :
                friend_list.append(relation.requestee)
            else:
                friend_list.append(relation.requestor)
        for relation in friend_request:
            if relation.requestor == me :
                friend_request_list.append(relation.requestee)
            else:
                friend_request_list.append(relation.requestor)
        print(friend_list)
        context['friend_list'] = friend_list
        context['friend_request_list'] = friend_request_list
        return context


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


# def post_list(request, pk):
#     user = CustomUser.objects.get(pk=pk)
#     post_list = Post.objects.filter(posted_by=user).order_by("-time")
#     post_list_json = serializers.serialize('json', post_list)
#     params = {
#         'post_list': post_list,
#         'post_list_json': post_list_json,
#     }
#     return render(request, 'asovi_app/post_list.html', params)


def my_page(request):
    try:
        get_object_or_404(NotificationSetting,user=request.user)
    except:
        NotificationSetting.objects.create(user=request.user)
    me = request.user
    my_profile = Profile.objects.get(user=me)
    friend_num = Friend.objects.filter(Q(requestor=me)|Q(requestee=me)).filter(friended=True).count()
    post = Post.objects.filter(posted_by=me).order_by("-time")
    post_num = post.count()
    post10 = post[0:10]
    posts_json = serializers.serialize('json',post)
    genre_json = serializers.serialize('json',Genre.objects.all().order_by('pk'))
    params = {
        'me': me,
        'profile': my_profile,
        'notification': count_new_events(me),
        'posts': post,
        'post10': post10,
        'friend_num': friend_num,
        'post_num': post_num,
        'posts_json': posts_json,
        'genre_json': genre_json,
    }
    return render(request, 'asovi_app/mypage.html', params)

def post_list(request,pk):
    try:
        get_object_or_404(NotificationSetting,user=request.user)
    except:
        NotificationSetting.objects.create(user=request.user)
    me = CustomUser.objects.get(pk=pk)
    my_profile = Profile.objects.get(user=me)
    friend_num = Friend.objects.filter(Q(requestor=me)|Q(requestee=me)).filter(friended=True).count()
    post = Post.objects.filter(posted_by=me).order_by("-time")
    post_num = post.count()
    post10 = post[0:10]
    posts_json = serializers.serialize('json',post)
    genre_json = serializers.serialize('json',Genre.objects.all().order_by('pk'))
    params = {
        'me': me,
        'profile': my_profile,
        'notification': count_new_events(me),
        'posts': post,
        'post10': post10,
        'friend_num': friend_num,
        'post_num': post_num,
        'posts_json': posts_json,
        'genre_json': genre_json,
    }
    return render(request, 'asovi_app/post_list.html', params)

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
    print(new_friend_request.count())
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
        'user':person
    }
    return render(request,'asovi_app/save_article.html',params)

def popular(request):
    Popular.objects.all().delete()
    data_all=Post.objects.all()
    for item in data_all:
        num=Post.objects.filter(place_id=item.place_id).count()
        place_name=item.place_name
        data_popular=Popular(num=num,place_name=place_name)
        if Popular.objects.filter(place_name=place_name).count==0:
            data_popular.save()
    data=Popular.objects.all().order_by('num')[0:5]
    params={
        'data':data
    }
    print(data)
    return render(request,'asovi_app/popular.html',params)

def settings(request):
    return render(request, 'asovi_app/settings.html')
