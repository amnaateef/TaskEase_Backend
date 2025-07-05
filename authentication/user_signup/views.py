from django.shortcuts import render, redirect

#from .forms import ExpertForm, CustomerForm

from django.contrib.auth.hashers import  make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from math import radians, sin, cos, sqrt, asin
from .models import Expert, Customer, Service, Review
from .serializers import ExpertSerializer, CustomerSerializer, PasswordChangeSerializer,ServiceCreateSerializer,ServiceSerializer,ExpertDetailSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer
from django.contrib.auth import login
from django.contrib.sessions.models import Session
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from user_signup.serializers import LandingServiceSerializer
from .serializers import ExpertSearchResultSerializer
from decimal import Decimal
import random


User = get_user_model()

def user_view(request):
    return render(request, 'user_form.html')

class CreateUserAPIView(APIView):
    def post(self, request):
        role = request.data.get("role")
        password = request.data.get("password")
        email = request.data.get("email")
        firstname = request.data.get("firstname")
        lastname = request.data.get("lastname")
        cnic = request.data.get("cnic")
        gender = request.data.get("gender")

        # Hash the password
        hashed_password = make_password(password)

        # Create the CustomUser
        user = User.objects.create(
            email=email,
            username=email,
            password=hashed_password,
            role=role,
            first_name=firstname,
            last_name=lastname,
            cnic=cnic,
            gender=gender
        )

        if role == "Expert":
            expert = Expert.objects.create(
                email=email,
                password=hashed_password,
                role=role,
                firstname=firstname,
                lastname=lastname,
                cnic=cnic,
                gender=gender,
                service_categories=request.data.get("service_categories"),
                years_of_experience=request.data.get("years_of_experience"),
                availability=request.data.get("availability"),
                phone_number=request.data.get("phone_number"),
                city=request.data.get("city"),
                longitude=request.data.get("longitude"),
                latitude=request.data.get("latitude"),
                starting_price=request.data.get("starting_price"),
                # Add any other fields as needed
            )
            return Response({"message": "Expert created successfully"}, status=status.HTTP_201_CREATED)

        elif role == "Customer":
            customer = Customer.objects.create(
                email=email,
                password=hashed_password,
                role=role,
                firstname=firstname,
                lastname=lastname,
                cnic=cnic,
                gender=gender,
                phone_number=request.data.get("phone_number"),
                city=request.data.get("city"),
                longitude=request.data.get("longitude"),
                latitude=request.data.get("latitude"),
                # Add any other fields as needed
            )
            return Response({"message": "Customer created successfully"}, status=status.HTTP_201_CREATED)

        else:
            user.delete()  # Clean up if invalid role
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            request.session["user_id"] = user.id
            request.session["role"] = user.role
            return Response({
                "message": "Login successful",
                "email": user.email,
                "role": user.role,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    # Expert Search and Fetching
'''class ExpertSearchView(APIView):
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
        return paginator.get_paginated_response(serializer.data)'''


# Review Views for creating and listing reviews
'''class ReviewCreateAPIView(APIView):
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''


'''class ReviewListAPIView(APIView):
    def get(self, request, expert_id):
        reviews = Review.objects.filter(expert_id=expert_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)'''


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
'''class TaskCreateAPIView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''


''''class TaskListAPIView(APIView):
    def get(self, request):
        tasks = Service.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)'''


'''class TaskDetailAPIView(APIView):
    def get(self, request, task_id):
        task = Service.objects.get(id=task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, task_id):
        task = Service.objects.get(id=task_id)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = Service.objects.get(id=task_id)
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)'''

'''class ExpertTasksAPIView(APIView):
    def get(self, request, expert_id):
        try:
            expert = Expert.objects.get(id=expert_id)
            tasks = Service.objects.filter(expert=expert)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expert.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)'''

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # This is the CustomUser instance from the token
        try:
            expert = Expert.objects.get(email=user.email)
            serializer = ExpertSerializer(expert)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expert.DoesNotExist:
            try:
                customer = Customer.objects.get(email=user.email)
                serializer = CustomerSerializer(customer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Customer.DoesNotExist:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user  # CustomUser from JWT
        try:
            try:
                expert = Expert.objects.get(email=user.email)
                serializer = ExpertSerializer(expert, data=request.data, partial=True)
            except Expert.DoesNotExist:
                try:
                    customer = Customer.objects.get(email=user.email)
                    serializer = CustomerSerializer(customer, data=request.data, partial=True)
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

'''class ExpertTasksView(APIView):
    def get(self, request):
        expert_id = request.session.get('user_id')
        if not expert_id:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            expert = Expert.objects.get(id=expert_id)
            tasks = Service.objects.filter(expert=expert)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expert.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)'''

'''class ExpertTasksListView(APIView):
    def get(self, request):
        tasks = Service.objects.all()
        paginator = PageNumberPagination()
        paginated_tasks = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(paginated_tasks, many=True)
        return paginator.get_paginated_response(serializer.data)'''

class ServiceCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user

        try:
            expert = Expert.objects.get(email=user.email)
        except Expert.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)

        selected_service = request.data.get("selected_service")

        serializer = ServiceCreateSerializer(
            data=request.data,
            context={"selected_service": selected_service}
        )

        if serializer.is_valid():
            service = serializer.save(expert=expert)

            # ✅ Append category safely (assumes JSONField)
            if selected_service:
                if not expert.service_categories:
                    expert.service_categories = []

                if selected_service not in expert.service_categories:
                    expert.service_categories.append(selected_service)
                    expert.save()

            return Response({"message": "Service created successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''class ServiceDeleteView(APIView):
    #permission_classes = [IsAuthenticated]

    def delete(self, request):
        user_id = request.session.get('user_id')
        role = request.session.get('role')

        if not user_id or role != "Expert":
            return Response({"error": "Unauthorized. Only experts can perform this action."}, status=status.HTTP_403_FORBIDDEN)

        category_to_remove = request.data.get("category")
        if not category_to_remove:
            return Response({"error": "Category is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expert = Expert.objects.get(user_id=user_id)
        except Expert.DoesNotExist:
            return Response({"error": "Expert profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Remove category from expert's service_categories
        if category_to_remove in expert.service_categories:
            expert.service_categories.remove(category_to_remove)
            expert.save()
        else:
            return Response({"error": f"'{category_to_remove}' not found in your service categories."}, status=status.HTTP_404_NOT_FOUND)

        # Delete all services of that category for this expert
        deleted_count, _ = Service.objects.filter(expert=expert, category=category_to_remove).delete()

        return Response({
            "message": f"Category '{category_to_remove}' removed from your profile and {deleted_count} service(s) deleted."
        }, status=status.HTTP_200_OK)'''

class ExpertServiceListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            expert = Expert.objects.get(email=request.user.email)
        except Expert.DoesNotExist:
            return Response({"error": "Expert not found"}, status=404)

        services = Service.objects.filter(expert=expert)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=200)
    
class LandingPageServiceListView(APIView):
    def get(self, request):
        services = Service.objects.select_related('expert').all().order_by('-created_at')
        serializer = LandingServiceSerializer(services, many=True)
        return Response(serializer.data, status=200)
    
class ExpertSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'Customer':
            return Response({"error": "Only customers can search experts."}, status=403)

        cities = request.query_params.get('cities', '')
        keywords = request.query_params.get('keywords', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        expert_queryset = Expert.objects.all()

        # Filter by cities
        if cities:
            city_list = [city.strip() for city in cities.split(',')]
            expert_queryset = expert_queryset.filter(city__in=city_list)

        # Filter by service keywords (JSONField)
        if keywords:
            keyword_list = [kw.strip().lower() for kw in keywords.split(',')]
            keyword_filter = Q()
            for kw in keyword_list:
                keyword_filter |= Q(service_categories__icontains=kw)
            expert_queryset = expert_queryset.filter(keyword_filter)

        # Filter by service price (from Expert.starting_price)
        if min_price:
            expert_queryset = expert_queryset.filter(starting_price__gte=Decimal(min_price))
        if max_price:
            expert_queryset = expert_queryset.filter(starting_price__lte=Decimal(max_price))

        serializer = ExpertSearchResultSerializer(expert_queryset, many=True)
        return Response(serializer.data, status=200)
    

class ServiceByCategoryView(APIView):
    def get(self, request):
        category_param = request.query_params.get('category', '')
        if not category_param:
            return Response({"error": "At least one category is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Split and clean category keywords
        categories = [cat.strip().lower() for cat in category_param.split(',') if cat.strip()]

        # Use Q for flexible OR filtering
        category_filter = Q()
        for cat in categories:
            category_filter |= Q(selected_service__iexact=cat)

        services = Service.objects.filter(category_filter).select_related('expert').order_by('-created_at')
        serializer = LandingServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RandomUniqueCategoryServicesView(APIView):
    def get(self, request):
        # Get all unique service categories
        unique_categories = Service.objects.values_list('selected_service', flat=True).distinct()

        # Shuffle categories randomly
        category_list = list(unique_categories)
        random.shuffle(category_list)

        # Pick up to 20 categories
        selected_categories = category_list[:20]

        # For each category, randomly pick 1 service
        result_services = []
        for cat in selected_categories:
            services_in_cat = list(Service.objects.filter(selected_service__iexact=cat))
            if services_in_cat:
                result_services.append(random.choice(services_in_cat))

        serializer = LandingServiceSerializer(result_services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ServiceExpertDetailView(APIView):
    def get(self, request):
        service_id = request.query_params.get('service_id')

        if not service_id:
            return Response({"error": "Service ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.select_related('expert').get(id=service_id)
            expert = service.expert
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpertDetailSerializer(expert)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteServiceView(APIView):
    def delete(self, request):
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response({"error": "Service ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.select_related('expert').get(id=service_id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

        expert = service.expert
        category_to_remove = service.selected_service.lower().strip()

        service.delete()

        if expert.service_categories:
            updated_categories = [
                cat for cat in expert.service_categories
                if cat.lower().strip() != category_to_remove
            ]
            expert.service_categories = updated_categories
            expert.save()

        return Response({"message": "Service deleted and category removed from expert."}, status=status.HTTP_200_OK)
    

'''class ServiceSearchView(APIView):
    def get(self, request):
        cities = request.query_params.get('cities', '')        # e.g. Lahore,Karachi
        services = request.query_params.get('services', '')    # e.g. Plumbing,Makeup
        min_price = request.query_params.get('min_price')      # e.g. 1000
        max_price = request.query_params.get('max_price')      # e.g. 5000

        queryset = Service.objects.all()

        if cities:
            city_list = [c.strip() for c in cities.split(',')]
            queryset = queryset.filter(city__in=city_list)

        if services:
            service_list = [s.strip().lower() for s in services.split(',')]
            service_filter = Q()
            for s in service_list:
                service_filter |= Q(selected_service__iexact=s)
            queryset = queryset.filter(service_filter)

        try:
            if min_price:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=Decimal(max_price))
        except:
            return Response({"error": "Invalid price range."}, status=400)

        serializer = LandingServiceSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)'''

class ServiceSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'Customer':
            return Response({"error": "Only customers can search services."}, status=403)

        cities = request.query_params.get('cities', '')
        services = request.query_params.get('services', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        queryset = Service.objects.all()

        
        if cities:
            city_list = [c.strip() for c in cities.split(',')]
            queryset = queryset.filter(city__in=city_list)

        
        if services:
            service_list = [s.strip().lower() for s in services.split(',')]
            service_filter = Q()
            for s in service_list:
                service_filter |= Q(selected_service__iexact=s)
            queryset = queryset.filter(service_filter)

        
        try:
            if min_price:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=Decimal(max_price))
        except:
            return Response({"error": "Invalid price range."}, status=400)

        serializer = LandingServiceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)