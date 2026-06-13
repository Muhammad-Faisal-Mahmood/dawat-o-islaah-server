# urls.py
from django.urls import path
from .views import (
    UserRegistrationAPIView,
    CustomTokenObtainPairView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    SetNewPasswordAPIView
)
from .views import ToggleDailyEmailAPIView
from .views import UpdateLocationAPIView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('setpassword/<str:uidb64>/<str:token>/', SetNewPasswordAPIView.as_view(),name='password-reset-complete'),
    path('toggle-daily-email/', ToggleDailyEmailAPIView.as_view(), name='toggle-daily-email'),
    path('update-location/', UpdateLocationAPIView.as_view(), name='update-location'),
]