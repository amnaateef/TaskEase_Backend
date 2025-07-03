from django.shortcuts import render

# Create your views here.
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_signup.models import Expert,Customer
from .serializers import ExpertSearchSerializer
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt,atan2
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from recommendation.models import SearchHistory
from .serializers import ServiceDetailSerializer


'''class ExpertSearchView(APIView):
    def get(self, request):
        keyword = request.query_params.get("keyword", "")
        city = request.query_params.get("city", "")
        domain = request.query_params.get("domain", "")
        price_min = request.query_params.get("price_min")
        price_max = request.query_params.get("price_max")
        rating_min = request.query_params.get("ratings_min")
        user_lat = request.query_params.get("latitude")
        user_lon = request.query_params.get("longitude")

        experts = Expert.objects.all()

        if keyword:
            experts = experts.filter(
                Q(firstname__icontains=keyword) |
                Q(lastname__icontains=keyword) |
                Q(domain__icontains=keyword)
            )

        if city:
            experts = experts.filter(city__iexact=city)

        if domain:
            experts = experts.filter(domain__iexact=domain)

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

                experts = [
                    e for e in experts
                    if e.latitude and e.longitude and
                    haversine(user_lat, user_lon, float(e.latitude), float(e.longitude)) <= radius_km
                ]
            except ValueError:
                pass
        paginator = PageNumberPagination()
        paginated_experts = paginator.paginate_queryset(experts, request)
        serializer = ExpertSearchSerializer(paginated_experts, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return paginator.get_paginated_response(serializer.data)'''

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

class ExpertSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if user is Customer
        if user.role != 'Customer':
            return Response(
                {"error": "Only customers can search for experts."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = Customer.objects.get(email=user.email)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Filters from query params
        category = request.query_params.get('keyword')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        min_rating = request.query_params.get('min_rating')

        if category:
            SearchHistory.objects.create(customer=customer, keyword=category)

        # Start with all experts
        experts = Expert.objects.all()

        # Filter by customer's city
        if customer.city:
            experts = experts.filter(city__iexact=customer.city)

        # Filter by service category
        if category:
            experts = experts.filter(service_categories__icontains=category)

        # Filter by price
        if min_price and max_price:
            experts = experts.filter(starting_price__gte=min_price, starting_price__lte=max_price)

        # Filter by minimum rating
        if min_rating:
            experts = experts.filter(ratings_average__gte=min_rating)

        # Filter by distance <= 500m from customer's lat/lon
        if customer.latitude and customer.longitude:
            user_lat = float(customer.latitude)
            user_lon = float(customer.longitude)
            nearby_experts = []

            for expert in experts:
                if expert.latitude and expert.longitude:
                    dist = calculate_distance(user_lat, user_lon, float(expert.latitude), float(expert.longitude))
                    if dist <= 500:
                        nearby_experts.append(expert)

            experts = nearby_experts

        serializer = ExpertSearchSerializer(experts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)