from django.shortcuts import render
from django.http import HttpResponse
from .forms import ProfileForm
from .models import Profile


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