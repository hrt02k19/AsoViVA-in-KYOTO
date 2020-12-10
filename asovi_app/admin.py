from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Genre)
admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(Post)
admin.site.register(Reply)
