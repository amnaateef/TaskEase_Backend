from django.urls import path
from .views import (
    CreateUserAPIView, user_view, ExpertSearchView,
    ReviewCreateAPIView, ReviewListAPIView, ProfileView,
    TaskCreateAPIView, TaskListAPIView, TaskDetailAPIView,
    ExpertTasksAPIView
)

urlpatterns = [
    path('create_user/', CreateUserAPIView.as_view(), name='create_user'),
    path('user/', user_view, name='user'),
    path('experts/search/', ExpertSearchView.as_view(), name='expert_search'),
    path('experts/<int:expert_id>/tasks/', ExpertTasksAPIView.as_view(), name='expert_tasks'),
    path('experts/<int:user_id>/profile/', ProfileView.as_view(), name='expert_profile'),
    path('reviews/create/', ReviewCreateAPIView.as_view(), name='create_review'),
    path('reviews/expert/<int:expert_id>/', ReviewListAPIView.as_view(), name='expert_reviews'),
    path('tasks/', TaskListAPIView.as_view(), name='task_list'),
    path('tasks/create/', TaskCreateAPIView.as_view(), name='create_task'),
    path('tasks/<int:task_id>/', TaskDetailAPIView.as_view(), name='task_detail'),
]