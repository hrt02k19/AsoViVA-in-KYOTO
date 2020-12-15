from typing import Counter
from django.db.models.query_utils import Q
from django.shortcuts import redirect, render

from allauth.exceptions import ImmediateHttpResponse
from allauth.account import app_settings
from allauth.account.views import SignupView
from allauth.account.utils import complete_signup

from .models import Block, Profile, CustomUserManager, Friend, CustomUser, Post
from .forms import CustomSignupForm, ProfileForm, PostForm, FindForm
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

def user_profile(request, pk):
    params = {
        'user': CustomUser.objects.get(pk=pk)
    }
    return render(request, 'asovi_app/user_profile.html', params)


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
    params = {
        'new_requests': Friend.objects.filter(friended=False, requestee=request.user)
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

def find_user(request):
    params = {}
    if request.method=='POST':
        form = FindForm(request.POST)
        find = request.POST['find']
        found_users = CustomUser.objects.filter(user_id__icontains=find)
        params = {
            'form': form,
            'found_users': found_users,
        }
    else:
        form = FindForm()
        params = {
            'form': form,
        }
    return render(request, 'asovi_app/find_user.html', params)

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
        'my_friend_requesting_num': len(my_friend_requesting),
        'my_friend_requested_num': len(my_friend_requested)
    }
    return render(request, 'asovi_app/friend_list.html', params)
