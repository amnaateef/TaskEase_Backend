from django.urls import path
from .views import ExpertSearchView
#from .views import ExpertServicesFromSearchView


urlpatterns = [
    path('search_experts/', ExpertSearchView.as_view(), name='search_experts'),
]
