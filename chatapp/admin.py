from django.contrib import admin
from chatapp.models import Room,Message,FriendRequest

class RoomAdmin(admin.ModelAdmin):
    list_display = ('id','name')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')  # Include any other fields you'd like to display


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender','receiver') 

admin.site.register(Room, RoomAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
