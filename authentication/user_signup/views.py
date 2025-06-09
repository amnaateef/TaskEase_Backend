from django.shortcuts import render, redirect

#from .forms import ExpertForm, CustomerForm

from django.contrib.auth.hashers import  make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ExpertSerializer, CustomerSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer


def user_view(request):
    return render(request, 'user_form.html')

class CreateUserAPIView(APIView):
    def post(self, request):
        role = request.data.get("role")
        password = request.data.get("password")
        
        # Hash the password
        hashed_password = make_password(password)

        if role == "Expert":
            serializer = ExpertSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(password=hashed_password)  # Save with hashed password
                return Response({"message": "Expert created successfully"}, status=status.HTTP_201_CREATED)

        elif role == "User":
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(password=hashed_password)  # Save with hashed password
                return Response({"message": "Customer created successfully"}, status=status.HTTP_201_CREATED)

        else:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)



