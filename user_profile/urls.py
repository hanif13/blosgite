from django.urls import path
from .views import*


urlpatterns = [
    path('login/', login_user, name='login'),
    path('registration/', registration_user, name='registration'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('change_profile_picture/', change_profile_picture, name='change_profile_picture'),
    path('user-profile/<str:username>/', view_user_information, name='view_user_information'),
    path('follow_or_unfolow/<int:user_id>', follow_or_unfolow_user, name='follow_or_unfolow'),
    path('notifications/', user_notifications, name='user_notifications'),
    path('mute_or_unmute/<int:user_id>/', mute_or_unmute, name='mute_or_unmute'),
]