from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Room, Message, FriendRequest
from ..serializers import RoomSerializer, MessageSerializer

class RoomView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id=None):
        """
        Retrieve all rooms or details of a specific room including its messages.
        """
        if room_id:
            room = Room.objects.filter(id=room_id).first()
            if not room:
                return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

            messages = Message.objects.filter(room=room)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)

        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def delete(self, request, room_id):
        """
        Delete a room if the user is authorized.
        Conditions:
        - User must have messages in the room or have a related friend request.
        """
        room = Room.objects.filter(id=room_id).first()
        if not room:
            return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        user_has_messages = Message.objects.filter(room=room, user=user).exists()
        related_friend_request = FriendRequest.objects.filter(
            sender=user
        ).exists() or FriendRequest.objects.filter(receiver=user).exists()

        if not user_has_messages and not related_friend_request:
            return Response(
                {"error": "You are not authorized to delete this room."},
                status=status.HTTP_403_FORBIDDEN
            )

        room.delete()
        if related_friend_request:
            FriendRequest.objects.filter(
                sender=user
            ).delete() or FriendRequest.objects.filter(receiver=user).delete()

        return Response(
            {"message": "Room deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
