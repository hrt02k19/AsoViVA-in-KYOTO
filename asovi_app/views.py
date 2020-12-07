from django.shortcuts import render
from django.http import HttpResponse
from .forms import ProfileForm,PostForm 
from .models import Profile,post
import datetime

# Create your views here.

def profile_edit(request):
    obj = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        profile = ProfileForm(request.POST, instance=obj)
        profile.save()
    params = {
        'form': ProfileForm(instance=obj),
    }
    return render(request,'asovi_app/profile_edit.html',params)



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
            posted=post(image=image,body=body,time=now,latitude=lat,longitude=lng)
        
            posted.save()
        

    return render(request,'asovi_app/post.html',params)