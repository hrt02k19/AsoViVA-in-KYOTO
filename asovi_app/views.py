from typing import Counter
from django.core import serializers
from django.db.models import Subquery, OuterRef
from django.db.models.query_utils import Q
from django.shortcuts import redirect, render
from django.views import generic

from allauth.exceptions import ImmediateHttpResponse
from allauth.account import app_settings
from allauth.account.views import SignupView
from allauth.account.utils import complete_signup

from .models import Block, Profile, CustomUserManager, Friend, CustomUser, Post
from .forms import CustomSignupForm, ProfileForm, PostForm
import datetime, random, string


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
                self.get_success_url(),
            )
        except ImmediateHttpResponse as e:
            return e.response


def profile_edit(request):
    obj = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        profile = ProfileForm(request.POST, instance=obj)
        profile.save()
    params = {
        'form': ProfileForm(instance=obj),
    }
    return render(request, 'asovi_app/profile_edit.html', params)


def post_view(request):

    params={
        'form':PostForm
    }
    if request.method=='POST':
        form=PostForm(request.POST)
        if form.is_valid():
            now=datetime.datetime.now()
            image=form.cleaned_data.get('image')
            body=form.cleaned_data.get('body')
            lat=form.cleaned_data.get('latitude')
            lng=form.cleaned_data.get('longitude')
            posted=Post(image=image,body=body,time=now,latitude=lat,longitude=lng)

            posted.save()

    return render(request,'asovi_app/post.html',params)

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
    new_requests = Friend.objects.filter(friended=False, requestee=request.user)
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
    params = {
        'new_requests': new_requests,
    }
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
    my_friend = Friend.objects.filter( Q(requestor=me) | Q(requestee=me)).filter(friended=True).order_by("-friended_date")
    my_friend_requesting = Friend.objects.filter(requestor=me,friended=False).order_by("-requested_date")
    my_friend_requested = Friend.objects.filter(requestee=me,friended=False).order_by("-requested_date")
    params = {
        'me': me,
        'friend': my_friend,
        'my_friend_requesting': my_friend_requesting,
        'my_friend_requested_num': len(my_friend_requested)
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
    profile = user.user_profile
    username = profile.username
    posts = Post.objects.all().exclude(posted_by__in=blocked_users)
    posts_json = serializers.serialize('json',posts)
    params = {
        'username': username,
        'posts': posts,
        'posts_json': posts_json,
    }
    return render(request,'asovi_app/post_map.html', params)

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
    profile = Profile.objects.get(user=user.pk)
    interested_genres = profile.interested_genre.all()
    params = {
        'me': me,
        'user': user,
        'profile': profile,
        'interested_genres': interested_genres,
    }
    return render(request, 'asovi_app/user_profile.html', params)


class PostListView(generic.ListView):
    model = Post
    template_name = 'asovi_app/post_list.html'

    def get_queryset(self, *args, **kwargs):
        me = self.request.user
        post_list = Post.objects.filter(posted_by=me).order_by("-time")
        return post_list
