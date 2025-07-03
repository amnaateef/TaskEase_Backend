from django.urls import path
from .views import CreateUserAPIView, user_view
from .views import CustomTokenObtainPairView
from .views import LoginView
from .views import UserProfileView
from .views import PasswordChangeView
from .views import ProfileUpdateView
from .views import NearbyExpertsView
#from .views import ExpertTasksView
#from .views import ExpertTasksListView
from .views import ServiceCreateView, ServiceDeleteView

urlpatterns = [
    path('create_user/', CreateUserAPIView.as_view(), name='create_user'),
    path('user/', user_view, name='user'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    path('update-profile/', ProfileUpdateView.as_view(), name='update_profile'),
    path('nearby-experts/', NearbyExpertsView.as_view(), name='nearby_experts'),
    #path('expert-tasks/', ExpertTasksView.as_view(), name='expert_tasks'),
    #path('expert-tasks-list/', ExpertTasksListView.as_view(), name='expert_tasks_list'),
    path('services/add/', ServiceCreateView.as_view(), name='add-service'),
    path('services/<int:listing_id>/delete/', ServiceDeleteView.as_view(), name='delete-service'),
]