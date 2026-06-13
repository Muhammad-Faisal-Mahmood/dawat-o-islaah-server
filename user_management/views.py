from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import User
from .utils import send_forget_password_email
from .serializers import (
    UserRegistrationSerializer,
    ChangePasswordSerializer,
    SetNewPasswordSerializer,
    UserLocationSerializer,
)


class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except serializers.ValidationError as e:
            if 'No active account found' in str(e):
                raise serializers.ValidationError({
                    "email": "User not found",
                    "password": "Invalid credentials"
                })
            raise e

        user = self.user
        
        # ✅ CAPTURE TIMEZONE FROM REQUEST AND SAVE TO USER
        # This reads the 'timezone' field sent from SignIn.jsx
        request = self.context.get('request')
        if request and request.data.get('timezone'):
            user.timezone = request.data.get('timezone')
            user.save(update_fields=['timezone'])

        data.update({
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'timezone': user.timezone, # ✅ Included in response
                'receive_daily_email': user.receive_daily_email,
                'latitude': user.latitude,   # ✅ Included in login response
                'longitude': user.longitude   # ✅ Included in login response
            }
        })
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ChangePasswordAPIView(generics.GenericAPIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(generics.GenericAPIView):
        def post(self, request):
            email = request.data.get("email")
            user = get_object_or_404(User, email=email)

            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = settings.CURRENT_SITE
            absurl = f'{current_site}setpassword/{uidb64}/{token}/'
            send_forget_password_email(user.first_name,email,absurl)
            return Response({'success': 'Password Reset Email Sent', 'message': 'We have sent you an email with a link to reset your password. Please check your inbox and follow the instructions to reset your password.'}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(generics.GenericAPIView):
    def patch(self, request,**kwargs):
        serializer=SetNewPasswordSerializer(data=request.data,context={'uid':kwargs['uidb64'],'token':kwargs['token']})
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class ToggleDailyEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.receive_daily_email = not user.receive_daily_email
        user.save()

        return Response({
            "message": "Preference updated successfully",
            "receive_daily_email": user.receive_daily_email
        }, status=status.HTTP_200_OK)


# ✅ NEW: API View to update User Coordinates
class UpdateLocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = UserLocationSerializer(instance=user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Location updated successfully",
                "latitude": user.latitude,
                "longitude": user.longitude
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
