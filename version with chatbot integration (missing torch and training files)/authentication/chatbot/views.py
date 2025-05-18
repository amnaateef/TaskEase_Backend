from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .chatbot_logic import chatbot_response  # Import the function

@api_view(['POST'])
def get_bot_reply(request):
    user_input = request.data.get("user_input")
    
    # Call chatbot response function
    bot_reply, _ = chatbot_response(user_input)
    
    return Response({"bot_reply": bot_reply})
