# chatbot/urls.py
from django.urls import path
from .views import get_bot_reply

urlpatterns = [
    path('get-bot-reply/', get_bot_reply, name='get_bot_reply'),
]
