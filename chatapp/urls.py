from django.urls import path
from chatapp.views import FriendRequestView,RoomView,FriendRequestUpdate

urlpatterns = [
    path('friend-request/', FriendRequestView.as_view(), name='friend_req'),
    path('friend-update/<int:request_id>/', FriendRequestUpdate.as_view(), name='friend_update'),
    path('room/', RoomView.as_view(), name='room'),
]