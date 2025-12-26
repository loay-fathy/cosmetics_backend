# views.py
from rest_framework import generics, permissions, status # Add status
from rest_framework.response import Response # Add Response
from rest_framework.views import APIView # Add APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model

# --- MODIFIED/NEW IMPORTS ---
from .serializers import RegisterSerializer, UserSerializer, EmailVerificationSerializer
from .utils import send_activation_email
# ----------------------------

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    # --- ADD THIS METHOD ---
    def perform_create(self, serializer):
        """
        Save the user instance (which is inactive) and send activation email.
        """
        user = serializer.save()
        try:
            send_activation_email(user)
        except Exception as e:
            # You should log this error in a real production app
            print(f"Error sending activation email: {e}")
            # Even if email fails, registration shouldn't fail
            # But you might want to handle this differently
            pass
    # -----------------------


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# --- ADD THIS NEW VIEW ---
class VerifyEmailView(APIView):
    """
    View to activate user account from email link.
    This is what your Next.js frontend will call.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        user.is_active = True
        user.save()
        
        return Response({"detail": "Email successfully verified. You can now log in."}, status=status.HTTP_200_OK)