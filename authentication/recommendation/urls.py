from django.urls import path
from .views import MLRecommendedServicesView

urlpatterns = [
    path('recommend-experts/', MLRecommendedServicesView.as_view(), name='recommend_experts'),
]