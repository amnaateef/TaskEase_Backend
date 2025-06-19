from django.urls import path
from .views import ExpertRecommendationView

urlpatterns = [
    path('recommend-experts/', ExpertRecommendationView.as_view(), name='recommend_experts'),
]