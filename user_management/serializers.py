import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from django.contrib.auth import authenticate

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    receive_daily_email = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'receive_daily_email', 'latitude', 'longitude', 'timezone')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            receive_daily_email=validated_data.get('receive_daily_email', True),
            latitude=validated_data.get('latitude'), # Added for location
            longitude=validated_data.get('longitude'), # Added for location
            timezone=validated_data.get('timezone', 'UTC') # Timezone from browser
        )
        return user

# ✅ NEW: Serializer specifically for updating location later
class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('latitude', 'longitude', 'timezone')
        extra_kwargs = {
            'latitude': {'required': True},
            'longitude': {'required': True}
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not authenticate(email=user.email, password=value):
            raise serializers.ValidationError("Incorrect old password.")
        return value
    
    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        special_characters = r'[!@#$%^&*()\-_=+{}\[\]|;:"<>,.?/]'
        special_characters_count = len(re.findall(special_characters, new_password))
        
        if old_password == new_password:
            raise serializers.ValidationError({
                  'Error': "New password must be different from the old password."
               })
        elif len(new_password) < 8:
          raise serializers.ValidationError({'Error':"Password must be at least 8 characters long."})
        
        elif special_characters_count < 1:
          raise serializers.ValidationError({'Error':"Password must contain at least 1 special character."})
        
        return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate(self, attrs):   
        password = attrs.get('password')
        token = self.context['token']
        uidb64 =self.context['uid']
        id = force_str(urlsafe_base64_decode(uidb64))
        
        user = get_object_or_404(User, id=id)
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError({'Error':"The reset link is invalid"})
        
        special_characters = r'[!@#$%^&*()\-_=+{}\[\]|;:"<>,.?/]'
        special_characters_count = len(re.findall(special_characters, password))
        
        if len(password) < 8:
            raise serializers.ValidationError({'Error':"Password must be at least 8 characters long."})
        
        elif special_characters_count < 1:
            raise serializers.ValidationError({'Error':"Password must contain at least 1 special character."})
        
        user.set_password(password)
        user.save()
        return user