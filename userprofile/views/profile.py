import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from userprofile.models import User, UserProfile,Hobby
from userprofile.serializers import OTPLoginSerializer, UserProfileSerializer,HobbySerializer
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets



# View to handle OTP login
class OTPLoginView(APIView):
    serializer_class = OTPLoginSerializer


    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        country_code = serializer.validated_data["country_code"]
        # Generate OTP
        otp = get_random_string(length=6, allowed_chars='0123456789')
        # Store OTP in session (or use a caching mechanism like Redis)
        request.session["otp"] = otp
        request.session["email"] = email
        request.session["country_code"] = country_code
        print(otp)
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
                <div class="otp-code">{otp}</div>
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
            message='Your OTP code is {otp}. It will expire in 5 minutes.',  # Fallback message
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

        print(f"Received OTP: {otp}")
        print(f"Stored OTP: {session_otp}")
        print(f"Email: {email}")
        print(f"Country Code: {country_code}")

        # Check if the country_code is None or empty
        if not country_code:
            return Response({"error": "Country code is missing!"}, status=status.HTTP_400_BAD_REQUEST)

        if otp == session_otp:
            try:
                user = User.objects.get(email=email)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({"message": "OTP verified successfully",'refresh': str(refresh),'access': str(access_token),}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                # Create user with email and country_code
                user = User.objects.create(email=email, country_code=country_code,is_active=True)
                user.save()
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({"message": "User created and logged in!",'refresh': str(refresh),'access': str(access_token),}, status=status.HTTP_200_OK)
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