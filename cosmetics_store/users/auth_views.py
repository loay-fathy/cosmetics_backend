# users/auth_views.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from cart.utils import merge_guest_cart_into_user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Accepts optional 'session_id' in the request data. After validating credentials,
    merges guest cart into the authenticated user's cart.
    """
    def validate(self, attrs):
        # This will authenticate and set self.user
        data = super().validate(attrs)

        # request is available in self.context when used by the view
        request = self.context.get('request')
        session_id = None
        if request:
            # accept session_id in body or header
            session_id = request.data.get('session_id') or request.headers.get('X-Session-Id')

        # merge if needed
        if session_id:
            try:
                merge_guest_cart_into_user(self.user, session_id)
            except Exception:
                # don't fail auth if merge fails; log in production
                pass

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
