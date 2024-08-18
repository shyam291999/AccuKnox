
from django.urls import path
from user.views import *



urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('send_request/<int:user_id>/', sendFriendRequest.as_view(), name='send_request'),
    path('respond_request/<int:friendship_id>/<str:action>/', AcceptUserRequest.as_view(), name='respond_request'),
    path('friends/', FriendListView.as_view(), name='friend_list'),
    path('pending_requests/', PendingFriendRequestsView.as_view(), name='pending_requests'),
]
    
