# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .auth_views import CustomTokenObtainPairView

# --- MODIFIED IMPORT ---
from .views import RegisterView, UserProfileView, VerifyEmailView
# -----------------------

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Remember my warning about this
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # --- ADD THIS NEW PATH ---
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    # -------------------------
]