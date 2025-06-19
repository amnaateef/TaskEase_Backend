from django.shortcuts import render, redirect
import logging
from django.db.models import Count
from math import radians, sin, cos, sqrt, atan2
import traceback

# Configure logging
logger = logging.getLogger(__name__)

    #from .forms import ExpertForm, CustomerForm

from django.contrib.auth.hashers import  make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ExpertSerializer, CustomerSerializer, LoginSerializer, 
    CustomTokenObtainPairSerializer, UserSerializer, 
    ProfileDetailSerializer, ExpertTaskSerializer, 
    ExpertWithTasksSerializer, ProfileUpdateSerializer,
    NearbyExpertSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Expert, Customer, Task
from django.contrib.auth import get_user_model
from .serializers import ProfileDetailSerializer
from .models import Task
from .serializers import ExpertTaskSerializer
from .serializers import ExpertWithTasksSerializer

User = get_user_model()

def user_view(request):
     return render(request, 'user_form.html')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CreateUserAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": f"{user.role} created successfully.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = ProfileDetailSerializer(request.user)
            logger.info(f"Profile data fetched successfully for user: {request.user.email}")
            return Response({
                "message": "Profile data retrieved successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching profile data for user {request.user.email}: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching profile data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordChangeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = PasswordChangeSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Password change validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                logger.warning(f"Invalid old password attempt for user: {user.email}")
                return Response(
                    {"old_password": "Current password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"Password successfully changed for user: {user.email}")
            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Unexpected error during password change: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            # Handle file upload separately
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                # Validate file type
                if not profile_picture.content_type.startswith('image/'):
                    logger.error(f"Invalid file type uploaded: {profile_picture.content_type}")
                    return Response(
                        {"profile_picture": "Only image files are allowed."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate file size (max 5MB)
                if profile_picture.size > 5 * 1024 * 1024:
                    logger.error(f"File too large: {profile_picture.size} bytes")
                    return Response(
                        {"profile_picture": "File size must be less than 5MB."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create a mutable copy of the data
            data = request.data.copy()
            if profile_picture:
                data['profile_picture'] = profile_picture

            # Log the incoming data for debugging
            logger.info(f"Updating profile for user {request.user.email} with data: {data}")

            serializer = ProfileUpdateSerializer(
                request.user,
                data=data,
                context={'request': request},
                partial=True
            )

            if not serializer.is_valid():
                logger.error(f"Profile update validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Save the updated profile
            updated_user = serializer.save()
            
            logger.info(f"Profile successfully updated for user: {request.user.email}")
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error during profile update: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": f"An unexpected error occurred while updating profile: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points using the Haversine formula
    Returns distance in meters
    """
    R = 6371000  # Earth's radius in meters

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

class NearbyExpertsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Check if user has location set
            if not request.user.latitude or not request.user.longitude:
                return Response({
                    "error": "User location not set",
                    "detail": "Please update your profile with your location to find nearby experts."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the current user's location
            try:
                user_lat = float(request.user.latitude)
                user_lon = float(request.user.longitude)
            except (ValueError, TypeError) as e:
                return Response({
                    "error": "Invalid user location",
                    "detail": "Your location coordinates are invalid. Please update your profile."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get all experts
            experts = Expert.objects.all()

            # Filter experts within 500 meters and calculate distances
            nearby_experts = []
            for expert in experts:
                try:
                    if expert.latitude and expert.longitude:
                        expert_lat = float(expert.latitude)
                        expert_lon = float(expert.longitude)
                        
                        distance = calculate_distance(user_lat, user_lon, expert_lat, expert_lon)
                        
                        if distance <= 500:  # 500 meters radius
                            expert.distance = round(distance, 2)
                            nearby_experts.append(expert)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid coordinates for expert {expert.id}: {str(e)}")
                    continue

            # Sort by distance
            nearby_experts.sort(key=lambda x: x.distance)

            # Serialize the data
            serializer = NearbyExpertSerializer(nearby_experts, many=True)
            
            logger.info(f"Successfully fetched {len(nearby_experts)} nearby experts for user: {request.user.email}")
            return Response({
                "message": f"Found {len(nearby_experts)} experts within 500 meters",
                "experts": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error fetching nearby experts: {str(e)}\nTraceback: {error_traceback}")
            return Response(
                {
                    "error": "An error occurred while fetching nearby experts.",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExpertTasksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get query parameters
            expert_id = request.query_params.get('expert_id')
            task_status = request.query_params.get('status')
            category = request.query_params.get('category')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')

            # Start with all tasks
            tasks = Task.objects.all()

            # Apply filters if provided
            if expert_id:
                tasks = tasks.filter(expert_id=expert_id)
            
            if task_status:
                tasks = tasks.filter(status=task_status)
            
            if category:
                tasks = tasks.filter(category=category)
            
            if min_price:
                tasks = tasks.filter(price__gte=min_price)
            
            if max_price:
                tasks = tasks.filter(price__lte=max_price)

            # Order by creation date (newest first)
            tasks = tasks.order_by('-created_at')

            # Get task statistics
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(status='completed').count()
            pending_tasks = tasks.filter(status='pending').count()
            in_progress_tasks = tasks.filter(status='in_progress').count()

            # Get unique experts count
            unique_experts = tasks.values('expert').distinct().count()

            # Serialize the tasks
            serializer = ExpertTaskSerializer(tasks, many=True)
            
            logger.info(f"Successfully fetched {total_tasks} tasks for user: {request.user.email}")
            return Response({
                "message": "Tasks retrieved successfully",
                "statistics": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "pending_tasks": pending_tasks,
                    "in_progress_tasks": in_progress_tasks,
                    "unique_experts": unique_experts
                },
                "filters_applied": {
                    "expert_id": expert_id,
                    "status": task_status,
                    "category": category,
                    "min_price": min_price,
                    "max_price": max_price
                },
                "tasks": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error fetching tasks: {str(e)}\nTraceback: {error_traceback}")
            return Response(
                {
                    "error": "An error occurred while fetching tasks.",
                    "detail": str(e),
                    "traceback": error_traceback
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExpertTasksListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get all experts with their tasks
            experts = Expert.objects.all()
            
            # Serialize the data
            serializer = ExpertWithTasksSerializer(experts, many=True)
            
            logger.info(f"Successfully fetched tasks for all experts")
            return Response({
                "message": "Expert tasks retrieved successfully",
                "experts": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error fetching expert tasks: {str(e)}\nTraceback: {error_traceback}")
            return Response(
                {
                    "error": "An error occurred while fetching expert tasks.",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    