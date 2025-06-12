

from django.urls import path
from .views import CreateUserAPIView,user_view
from .views import CustomTokenObtainPairView
from .views import LoginView
from .views import UserProfileView



urlpatterns = [
   path('create_user/', CreateUserAPIView.as_view(), name='create_user'),
   path('user/', user_view, name='user'),
  path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('login/', LoginView.as_view(), name='login'),  # 👈 ADD THIS
    path('profile/', UserProfileView.as_view(), name='profile'),  # 👈 ADD THIS
]