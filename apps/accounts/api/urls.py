from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from django.urls import path, include
from .views.google_views import GoogleJWTview
from .views.auth_views import RegistratoinView, VerifyOtp, RegenerateOtp

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/token/", TokenRefreshView.as_view(), name="refresh-token"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("", include("allauth.urls")),
    path("google/jwt/", GoogleJWTview.as_view(), name="google-jwt"),
    path("registration/", RegistratoinView.as_view(), name="registration"),
    path("verify_otp/", VerifyOtp.as_view(), name="verify_otp"),
    path("regenerate_otp/", RegenerateOtp.as_view(), name="regenerate_otp"),
]
