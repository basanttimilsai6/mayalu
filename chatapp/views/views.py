from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Room, Message
from django.contrib.auth.models import User
from ..serializers import RoomSerializer, MessageSerializer

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Room, Message,FriendRequest
from django.contrib.auth.models import User
from ..serializers import RoomSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication



class RoomView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id=None):
        # Retrieve rooms or specific room details
        if room_id:
            try:
                room = Room.objects.get(id=room_id)
                messages = Message.objects.filter(room=room)
                serializer = MessageSerializer(messages,many=True)
                return Response(serializer.data)
            except Room.DoesNotExist:
                return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            rooms = Room.objects.all()
            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data)

    def delete(self, request, room_id):
        user = request.user
        try:
            # Fetch the room
            room = Room.objects.get(id=room_id)
            
            # Fetch the friend request (as sender or receiver)
            friend_req = FriendRequest.objects.filter(sender=user) | FriendRequest.objects.filter(receiver=user)
            
            # Check if user has no messages in the room and no friend request exists
            if not room.messages.filter(user=user).exists() and not friend_req.exists():
                return Response(
                    {"error": "You are not authorized to delete this room."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete the room and related friend request
            room.delete()
            friend_req.delete()
            
            return Response(
                {"message": "Room deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Room.DoesNotExist:
            return Response(
                {"error": "Room not found."},
                status=status.HTTP_404_NOT_FOUND
            )