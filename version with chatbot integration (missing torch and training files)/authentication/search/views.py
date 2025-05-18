from django.shortcuts import render

# Create your views here.
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_signup.models import Expert
from .serializers import ExpertSearchSerializer
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

class ExpertSearchView(APIView):
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
        return paginator.get_paginated_response(serializer.data)
