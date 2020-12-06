from django.urls import path

from . import views

app_name = 'asovi_app'
urlpatterns = [
    path('accounts/signup/', views.MySignupView.as_view(), name='account_signup'),
    path('profile_edit/',views.profile_edit,name='profile-edit'),
    path('post/',views.post_view,name='post'),

]
