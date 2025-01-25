from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from userprofile.models import User
from django.db.models import Q
from chatapp.models import FriendRequest, Room
from chatapp.serializers import FriendRequestSerializer

class FriendRequestView(APIView):
    """
    API view to handle sending, accepting, and rejecting friend requests.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all friend requests received by the authenticated user.
        """
        friend_requests = FriendRequest.objects.filter(receiver=request.user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Send a friend request to another user.
        """
        sender = request.user
        receiver_id = request.data.get('receiver_id')
        
        if not receiver_id:
            return Response({"error": "Receiver ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)

            # Check for any existing relationship or pending requests
            if FriendRequest.objects.filter(
                Q(sender=sender, receiver=receiver) |
                Q(sender=receiver, receiver=sender)
            ).exists():
                return Response({"error": "Friend request already exists or you are already friends."}, status=status.HTTP_400_BAD_REQUEST)

            # Create friend request
            friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)

    # def put(self, request, request_id):
    #     """
    #     Accept a friend request.
    #     """
    #     try:
    #         friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user)
    #         friend_request.is_accepted = True
    #         friend_request.save()

    #         # Create or update a chat room for the new friends
    #         room, _ = Room.objects.get_or_create()
    #         room.users.add(friend_request.sender, friend_request.receiver)

    #         return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

    #     except FriendRequest.DoesNotExist:
    #         return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, request_id):
        """
        Reject or delete a friend request.
        """
        try:
            friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user)
            friend_request.delete()
            return Response({"message": "Friend request rejected."}, status=status.HTTP_204_NO_CONTENT)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

class FriendRequestUpdate(APIView):
    """
    API view to handle sending, accepting, and rejecting friend requests.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        """
        Accept a friend request.
        """
        user = User.objects.get(email=request.user)
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
            friend_request.is_accepted = True
            friend_request.save()

            # Create or update a chat room for the new friends
            room, _ = Room.objects.get_or_create()
            room.users.add(friend_request.sender, friend_request.receiver)

            return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

        89