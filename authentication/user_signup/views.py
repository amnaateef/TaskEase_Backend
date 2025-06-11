from django.shortcuts import render, redirect

#from .forms import ExpertForm, CustomerForm

from django.contrib.auth.hashers import  make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from math import radians, sin, cos, sqrt, asin
from .models import Expert, Customer, Task, Review
from .serializers import ExpertSerializer, CustomerSerializer, TaskSerializer, ReviewSerializer, ExpertSearchSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer
from django.contrib.auth import login
from django.contrib.sessions.models import Session
from django.middleware.csrf import get_token


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

        elif role == "Customer":
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(password=hashed_password)  # Save with hashed password
                return Response({"message": "Customer created successfully"}, status=status.HTTP_201_CREATED)

        else:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)'''

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            request.session["user_id"] = user.id
            request.session["role"] = user.role
            return Response({
                "message": "Login successful",
                "email": user.email,
                "role": user.role,
                #"csrf_token": get_token(request)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    # Expert Search and Fetching
class ExpertSearchView(APIView):
    def get(self, request):
        keyword = request.query_params.get("keyword", "")
        city = request.query_params.get("city", "")
        price_min = request.query_params.get("price_min")
        price_max = request.query_params.get("price_max")
        rating_min = request.query_params.get("ratings_min")
        user_lat = request.query_params.get("latitude")
        user_lon = request.query_params.get("longitude")

        experts = Expert.objects.all()

        if keyword:
            experts = experts.filter(
                Q(firstname__icontains=keyword) |
                Q(lastname__icontains=keyword)
            )

        if city:
            experts = experts.filter(city__iexact=city)

        if price_min:
            try:
                price_min = float(price_min)
                experts = experts.filter(starting_price__gte=price_min)
            except ValueError:
                pass

        if price_max:
            try:
                price_max = float(price_max)
                experts = experts.filter(starting_price__lte=price_max)
            except ValueError:
                pass

        if rating_min:
            try:
                rating_min = float(rating_min)
                experts = experts.filter(ratings_average__gte=rating_min)
            except ValueError:
                pass

        if user_lat and user_lon:
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                radius_km = 10

                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371
                    dlat = radians(lat2 - lat1)
                    dlon = radians(lon2 - lon1)
                    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
                    c = 2 * asin(sqrt(a))
                    return R * c

                experts = [e for e in experts if e.latitude and e.longitude and
                    haversine(user_lat, user_lon, float(e.latitude), float(e.longitude)) <= radius_km]
            except ValueError:
                pass
        
        paginator = PageNumberPagination()
        paginated_experts = paginator.paginate_queryset(experts, request)
        serializer = ExpertSearchSerializer(paginated_experts, many=True)
        return paginator.get_paginated_response(serializer.data)


# Review Views for creating and listing reviews
class ReviewCreateAPIView(APIView):
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewListAPIView(APIView):
    def get(self, request, expert_id):
        reviews = Review.objects.filter(expert_id=expert_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Profile View for fetching and updating profiles
class ProfileView(APIView):
    def get(self, request, user_id):
        user = Expert.objects.get(id=user_id)  # Fetch the expert by ID (can also be Customer)
        serializer = ExpertSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = Expert.objects.get(id=user_id)
        serializer = ExpertSerializer(user, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Task Views (CRUD operations for tasks)
class TaskCreateAPIView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListAPIView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskDetailAPIView(APIView):
    def get(self, request, task_id):
        task = Task.objects.get(id=task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, task_id):
        task = Task.objects.get(id=task_id)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = Task.objects.get(id=task_id)
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class ExpertTasksAPIView(APIView):
    def get(self, request, expert_id):
        try:
            expert = Expert.objects.get(id=expert_id)
            tasks = Task.objects.filter(expert=expert)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expert.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)