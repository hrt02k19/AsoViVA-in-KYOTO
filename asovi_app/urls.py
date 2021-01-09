from django.urls import path

from . import views

app_name = 'asovi_app'
urlpatterns = [
    path('look/<id>/<user>/',views.look,name='look'),
    path('accounts/signup/', views.MySignupView.as_view(), name='account_signup'),
    path('profile_edit/',views.profile_edit,name='profile_edit'),
    path('post/', views.post_view, name='post'),
    path('post_completed/<int:pk>', views.post_completed, name='post_completed'),
    path('post_detail/<int:pk>/',views.post_detail,name='post_detail'),
    path('post_list/<int:pk>/', views.post_list, name='post_list'),
    path('user_profile/<int:pk>/', views.user_profile, name='user_profile'),
    path('friend_request/<int:pk>/', views.friend_request, name='friend_request'),
    path('friend_request_accept/', views.friend_request_accept, name='friend_request_accept'),
    path('friend_list/',views.friend_list, name='friend_list'),
    path('friend_block/<int:pk>/',views.friend_block, name='friend_block'),
    path('post_map/', views.post_map, name='post_map'),
    path('place_detail/<str:place_id>/', views.place_detail, name='place_detail'),
    path('find_user/', views.FindUserView.as_view(), name='find_user'),
    path('check_event/', views.check_event, name='check_event'),
    path('notification_setting/',views.notification_setting, name='notification_setting'),
    path('my_page/', views.my_page, name='my_page'),
    path('email/change/', views.EmailChange.as_view(), name='change_email'),
    path('email/change/email_sent/', views.change_email_sent, name='change_email_sent'),
    path('email/change/completed/<str:token>/', views.EmailChangeComplete.as_view(), name='change_email_completed'),
    path('id/change/', views.change_id, name='change_id'),
    path('id/change/completed', views.change_id_completed, name='change_id_completed'),
    path('accounts/logout/completed/', views.logout_completed, name='logout_completed'),
    path('signout/', views.signout, name='signout'),
    path('signout/completed/', views.signout_completed, name='signout_completed'),
    path('contact/',views.contact,name='contact'),
    path('save_article/',views.save_article,name='save_article'),
    path('contact_fin/', views.contact_fin, name='contact_fin'),
    path('settings/', views.settings, name='settings'),
]
