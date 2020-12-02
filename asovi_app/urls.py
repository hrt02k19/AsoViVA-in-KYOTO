from django.urls import path

from . import views

app_name = 'asovi_app'
urlpatterns = [
    path('',views.IndexView.as_View(),name="index"),
]