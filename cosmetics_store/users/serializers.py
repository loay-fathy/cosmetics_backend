# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# --- Add these imports ---
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from .tokens import account_activation_token
# -------------------------

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password2', 'phone', 
                  'governorate', 'city', 'address_detail')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        
        # --- MODIFICATION ---
        # User is created as inactive until they verify their email
        user = User.objects.create_user(**validated_data, is_active=False)
        # --------------------
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone', 
                  'governorate', 'city', 'address_detail')

# --- ADD THIS NEW SERIALIZER ---
class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for verifying email.
    Takes uidb64 and token.
    """
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Invalid activation link.')

        if not account_activation_token.check_token(user, attrs['token']):
            raise serializers.ValidationError('Invalid activation link.')

        attrs['user'] = user
        return attrs