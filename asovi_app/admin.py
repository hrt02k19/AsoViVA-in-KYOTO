from django.contrib import admin

from .models import CustomUser, Profile, Genre
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Genre)
admin.site.register(Profile)
