from django.shortcuts import render, redirect

#from .forms import ExpertForm, CustomerForm

from django.contrib.auth.hashers import  make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from math import radians, sin, cos, sqrt, asin
from .models import Expert, Customer, Task, Review
from .serializers import ExpertSerializer, CustomerSerializer, TaskSerializer, ReviewSerializer, ExpertSearchSerializer, PasswordChangeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer
from django.contrib.auth import login
from django.contrib.sessions.models import Session
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model

User = get_user_model()

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

class PasswordChangeView(APIView):
    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Get user from session or request
            user_id = request.session.get('user_id')
            if not user_id:
                return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                # Try to get user from both Expert and Customer models
                try:
                    user = Expert.objects.get(id=user_id)
                except Expert.DoesNotExist:
                    try:
                        user = Customer.objects.get(id=user_id)
                    except Customer.DoesNotExist:
                        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
                # Verify old password
                if not check_password(old_password, user.password):
                    return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Update password
                user.password = make_password(new_password)
                user.save()
                
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginSerializer

class UserProfileView(APIView):
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            try:
                user = Expert.objects.get(id=user_id)
            except Expert.DoesNotExist:
                try:
                    user = Customer.objects.get(id=user_id)
                except Customer.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ExpertSerializer(user) if isinstance(user, Expert) else CustomerSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileUpdateView(APIView):
    def put(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            try:
                user = Expert.objects.get(id=user_id)
                serializer = ExpertSerializer(user, data=request.data, partial=True)
            except Expert.DoesNotExist:
                try:
                    user = Customer.objects.get(id=user_id)
                    serializer = CustomerSerializer(user, data=request.data, partial=True)
                except Customer.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NearbyExpertsView(APIView):
    def get(self, request):
        user_lat = request.query_params.get("latitude")
        user_lon = request.query_params.get("longitude")
        radius_km = request.query_params.get("radius", 10)
        
        if not user_lat or not user_lon:
            return Response({"error": "Latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            radius_km = float(radius_km)
            
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                return R * c
            
            experts = Expert.objects.filter(latitude__isnull=False, longitude__isnull=False)
            nearby_experts = []
            
            for expert in experts:
                distance = haversine(user_lat, user_lon, float(expert.latitude), float(expert.longitude))
                if distance <= radius_km:
                    expert_data = ExpertSerializer(expert).data
                    expert_data['distance_km'] = round(distance, 2)
                    nearby_experts.append(expert_data)
            
            # Sort by distance
            nearby_experts.sort(key=lambda x: x['distance_km'])
            
            return Response(nearby_experts, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExpertTasksView(APIView):
    def get(self, request):
        expert_id = request.session.get('user_id')
        if not expert_id:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            expert = Expert.objects.get(id=expert_id)
            tasks = Task.objects.filter(expert=expert)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expert.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExpertTasksListView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        paginator = PageNumberPagination()
        paginated_tasks = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(paginated_tasks, many=True)
        return paginator.get_paginated_response(serializer.data)