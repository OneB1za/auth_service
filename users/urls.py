from . import views
from django.urls import path

app_name = 'users'

urlpatterns = [
    path('profile/<slug:username>/', views.UserProfileView.as_view(), name='user_profile'),
    # path('alarms/'),
    # path('settings/'),
    # path('settings/privacy'),
    path('settings/', views.UserProfileSettingsView.as_view(), name='profile_settings'),
    path('friendlist/<slug:username>/', views.FriendlistView.as_view(), name='friendlist'),
    path('remove-friend/<slug:username>/', views.RemoveFriendView.as_view(), name='remove_friend'),
    path('accept-request-friend/', views.AcceptFriendView.as_view() , name='accept_request_friend'),
    path('reject-request-friend/', views.RejectFriendView.as_view(), name='reject_request_friend'),
    path('my-requested-friend/', views.GetMyRequestedFriendsView.as_view(), name='my_requested_friend'),
    path('add-friend/', views.AddFriendView.as_view(), name='add_friend'),
    path('login/', views.login_view, name='login'),
    path('register/', views.registration_view, name='register'),
    path('logout/', views.logout_view, name='logout')
    # капча + емейл?
]
