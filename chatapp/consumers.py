import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message
from userprofile.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"WebSocket connect: {self.scope['url_route']}")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Extract user email from query string
        query_params = self.scope["query_string"].decode("utf-8")
        query_dict = dict(param.split('=') for param in query_params.split('&') if '=' in param)
        user_email = query_dict.get('email')  # User email sent in query params

        query_params = self.scope["query_string"].decode("utf-8")
        print("Query String:", query_params)
        query_dict = dict(param.split('=') for param in query_params.split('&') if '=' in param)
        print("Query Dict:", query_dict)
        user_email = query_dict.get('email')
        print("User  Email:", user_email)

        # Check if room exists
        room = await self.get_room(self.room_name)
        if not room:
            print(f"Room does not exist: {self.room_name}")
            await self.close()  # Reject connection if room doesn't exist
            return
        print(user_email)

        # Check if the user is associated with the room
        if not await self.is_user_in_room(user_email, room):
            print(f"User with email {user_email} is not part of the room {self.room_name}")
            await self.close()  # Reject connection if the user is not part of the room
            return

        # Add this channel to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            print(f"Received text_data: {text_data}")
            if not text_data:
                print("No data received.")
                return

            data = json.loads(text_data)

            # Extract data fields
            message = data.get('message')
            username = data.get('username')
            room_name = data.get('room')

            if not (message and username and room_name):
                print("Missing required fields in the data.")
                return

            # Save the message first
            await self.save_message(username, room_name, message)

            # Broadcast the message to other clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )
        except Exception as e:
            print(f"Error in receiving message: {e}")



    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

    @sync_to_async
    def save_message(self, username, room_name, message):
        print(username,message,room_name)
        try:
            user = User.objects.get(email=username)
            room = Room.objects.get(name=room_name)

            # Check if the user is part of the room before saving the message
            if room.users.filter(id=user.id).exists():
                Message.objects.create(user=user, room=room, content=message)
            else:
                print(f"User with email {username} is not part of the room {room_name}.")
        except User.DoesNotExist:
            print(f"User with email {username} does not exist.")
        except Room.DoesNotExist:
            print(f"Room with name {room_name} does not exist.")

    @sync_to_async
    def get_room(self, room_name):
        try:
            room = Room.objects.get(name=room_name)
            print(f"Room exists: {room}")
            return room
        except Room.DoesNotExist:
            return None

    @sync_to_async
    def is_user_in_room(self, email, room):
        try:
            user = User.objects.get(email=email)
            return room.users.filter(id=user.id).exists()
        except User.DoesNotExist:
            return False
