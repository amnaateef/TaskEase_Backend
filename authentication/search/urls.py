from django.urls import path
from .views import ExpertSearchView

urlpatterns = [
    path('search_experts/', ExpertSearchView.as_view(), name='search_experts'),
]
