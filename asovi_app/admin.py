from django.contrib import admin

from .models import Profile,Genre,Good,Save
# Register your models here.

admin.site.register(Genre)
admin.site.register(Profile)
admin.site.register(Good)
admin.site.register(Save)