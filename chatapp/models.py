from django.contrib.auth.models import User
from django.db import models
import uuid



class Room(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name='users')

    def __str__(self):
        return self.name  # This is just an example, customize as needed
    
    def save(self, *args, **kwargs):
        # Automatically generate a unique room_name if it is not already set
        if not self.name:
            self.name = str(uuid.uuid4())
        super().save(*args, **kwargs)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')  # Prevent duplicate friend requests

    def __str__(self):
        return f"FriendRequest from {self.sender} to {self.receiver}"
