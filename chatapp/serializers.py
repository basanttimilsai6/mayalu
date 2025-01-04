from rest_framework import serializers
from .models import Room, Message
from userprofile.models import User
from .models import FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'sender', 'receiver', 'is_accepted', 'created_at')
        read_only_fields = ('id', 'sender', 'created_at', 'is_accepted')

        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'slug')

class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'room', 'user', 'content', 'date_added')
