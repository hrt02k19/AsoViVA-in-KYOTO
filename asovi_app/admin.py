from django.contrib import admin

from .models import Profile,Genre
# Register your models here.

admin.site.register(Genre)
admin.site.register(Profile)