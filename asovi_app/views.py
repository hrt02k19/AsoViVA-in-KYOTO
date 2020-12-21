from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import ProfileForm,PostForm ,GoodForm,SaveForm
from .models import Profile,post,Good,Save

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
        'form':PostForm(),
    }
    if request.method=='POST':
        form=PostForm(request.POST)
        if form.is_valid():
            user=request.user
            genre=form.cleaned_data('genre')

            now=datetime.datetime.now()
            image=form.cleaned_data.get('image')
            body=form.cleaned_data.get('body')
            lat=form.cleaned_data.get('latitude')
            lng=form.cleaned_data.get('longitude')
            posted=post(image=image,body=body,time=now,latitude=lat,longitude=lng,user=user,genre=genre)
        
            posted.save()
            return redirect(to='post') #投稿後に遷移するページが完成次第post/から変更する
        

    return render(request,'asovi_app/post.html',params)



def look(request,id,user):
    data=Good.objects.filter(article=id,user=user)
    post_data=post.objects.filter(id=id)
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