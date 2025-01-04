from rest_framework import serializers

class YouTubeShortSerializer(serializers.Serializer):
    video_id = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=255)
    thumbnail_url = serializers.URLField()
    video_url = serializers.URLField()
