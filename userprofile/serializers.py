from rest_framework import serializers
from userprofile.models import User, UserProfile,Hobby,OTP

class OTPLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['user', 'code']

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'country_code', 'password', 'is_active', 'is_staff']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)