from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenBlacklistView
from django.urls import path

urlpattens = [
    path('login/',TokenObtainPairView.as_view(),name='login'),
    path('refresh/token/',TokenRefreshView.as_view(),name='refresh-token'),
    path('logout/',TokenBlacklistView.as_view(),name='logout'),
]