import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from userprofile.models import User, UserProfile,Hobby,OTP
from userprofile.serializers import OTPLoginSerializer, UserProfileSerializer,HobbySerializer,UserSerializer
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from django.contrib.auth import get_user_model


# View to handle OTP login
class OTPLoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        country_code = request.data.get("country_code")

        if not email or not country_code:
            return Response(
                {"error": "Email and country code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate a 6-digit OTP code
        otp_code = get_random_string(length=6, allowed_chars='0123456789')

        try:
            # Attempt to find the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # If the user doesn't exist, create a new one
            user = User.objects.create(email=email, country_code=country_code)

        # Update or create the OTP for the user
        try:
            otp = OTP.objects.get(user=user)
            otp.code = otp_code
            otp.save()
        except OTP.DoesNotExist:
            OTP.objects.create(user=user, code=otp_code)

        request.session["otp"] = otp_code
        request.session["email"] = email
        request.session["country_code"] = country_code
        print(otp_code)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    color: #333;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                h2 {{
                    color: #007bff;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: #555;
                }}
                .otp-code {{
                    font-size: 24px;
                    color: #007bff;
                    margin: 10px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #888;
                    margin-top: 20px;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 15px;
                    font-size: 16px;
                    color: #ffffff;
                    background-color: #007bff;
                    border-radius: 5px;
                    text-decoration: none;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <h2>OTP Verification</h2>
                <p>Dear User,</p>
                <p>Your one-time password (OTP) for login is:</p>
                <div class="otp-code">{otp_code}</div>
                <p>Please use this OTP to complete your login. It will expire in <strong>5 minutes</strong>.</p>
                <hr>
                <p>If you did not request this, please ignore this email or contact support.</p>
                <div class="footer">
                    <p>Thank you for using our service.<br><a href="https://yourwebsite.com">Your Company Name</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Send the email
        send_mail(
            subject='OTP Code',
            message='Your OTP code is {otp_code}. It will expire in 5 minutes.',  # Fallback message
            from_email='viewaworld6@gmail.com',  # From email
            recipient_list=[email],  # To email
            html_message=html_content,  # HTML content
        )
        
        return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        email = request.session.get("email")
        session_otp = request.session.get("otp")
        country_code = request.session.get("country_code")

        # Ensure OTP and email exist in the session before verifying
        if not otp:
            return Response({"error": "OTP is required!"}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Email is missing!"}, status=status.HTTP_400_BAD_REQUEST)
        if not session_otp:
            return Response({"error": "Session OTP is missing!"}, status=status.HTTP_400_BAD_REQUEST)
        if not country_code:
            return Response({"error": "Country code is missing!"}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Received OTP: {otp}")
        print(f"Stored OTP: {session_otp}")
        print(f"Email: {email}")
        print(f"Country Code: {country_code}")

        # Check if the received OTP matches the session OTP
        if otp != session_otp:
            return Response({"error": "Invalid OTP!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user associated with the OTP
            user = User.objects.get(email=email)
            print(user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response(
                {
                    "message": "OTP verified successfully",
                    'refresh': str(refresh),
                    'access': access_token,
                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response({"error": "Invalid OTP!"}, status=status.HTTP_400_BAD_REQUEST)





class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        return Response({"message": "Hahhaa yes!"}, status=status.HTTP_200_OK)
    

# ViewSet for UserProfile CRUD operations
class UserProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class HobbyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer