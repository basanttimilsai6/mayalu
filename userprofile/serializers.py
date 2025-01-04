from rest_framework import serializers
from .models import User, UserProfile,Hobby

class OTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    country_code = serializers.CharField(max_length=5)

class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = ['id', 'name']  # Adjust fields based on your model

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    hobbies = serializers.PrimaryKeyRelatedField(queryset=Hobby.objects.all(), many=True)  # Use existing hobbies

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'full_name', 'hobbies', 'address', 
            'gender', 'nickname', 'profile_image', 'phone_number', 
            'date_of_birth', 'social_media_links'
        ]