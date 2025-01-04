from django.urls import path
from rest_framework.routers import DefaultRouter
from userprofile.views import OTPLoginView, VerifyOTPView, UserProfileViewSet,HobbyViewSet

urlpatterns = [
    path("otp/login/", OTPLoginView.as_view(), name="otp-login"),
    path("otp/verify/", VerifyOTPView.as_view(), name="otp-verify"),
]

from django.urls import path, include

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'hobbies', HobbyViewSet, basename='hobby')

urlpatterns += [
    path('api/', include(router.urls)),  # Include the router URLs
]