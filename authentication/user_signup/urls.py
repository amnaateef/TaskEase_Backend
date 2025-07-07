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
from .views import ServiceCreateView
from .views import ExpertServiceListView
from .views import LandingPageServiceListView
from .views import ExpertSearchView
from .views import ServiceByCategoryView
from .views import RandomUniqueCategoryServicesView
from .views import ServiceExpertDetailView
from .views import DeleteServiceView
from .views import ServiceSearchView
from .views import CreateReservationView
from .views import ExpertAssignedServicesView
from .views import ExpertUpdateBookingStatusView


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
    #path('services/<int:listing_id>/delete/', ServiceDeleteView.as_view(), name='delete-service'),
    path('my-services/', ExpertServiceListView.as_view(), name='expert-services'),
    path('landing-services/', LandingPageServiceListView.as_view(), name='landing-services'),
    path('search-experts/', ExpertSearchView.as_view(), name='search-experts'),
    path('services-by-category/', ServiceByCategoryView.as_view(), name='services-by-category'),
    path('random-unique-services/', RandomUniqueCategoryServicesView.as_view(), name='random-unique-services'),
    path('service-expert/', ServiceExpertDetailView.as_view(), name='service-expert'),
    path('delete-service/', DeleteServiceView.as_view(), name='delete-service'),
    path('search-services/', ServiceSearchView.as_view(), name='search-services'),
    path('create-reservation/', CreateReservationView.as_view(), name='create-reservation'),
    path('expert/assigned-services/', ExpertAssignedServicesView.as_view(), name='expert-assigned-services'),
    path('expert/update-booking-status/', ExpertUpdateBookingStatusView.as_view(), name='expert-update-booking-status'),
]