from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from user_signup.models import Customer, Expert,Booking
from .models import SearchHistory
from user_signup.serializers import NearbyExpertSerializer
from search.views import calculate_distance  # reuse your existing distance function
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ExpertRecommendationSerializer


class ExpertRecommendationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Ensure user is a customer
        try:
            customer = Customer.objects.get(email=user.email)
        except Customer.DoesNotExist:
            return Response({"error": "Only customers can receive recommendations."}, status=403)

        if not customer.latitude or not customer.longitude:
            return Response({"error": "Customer location is missing."}, status=400)

        user_lat = float(customer.latitude)
        user_lon = float(customer.longitude)

        # 2. Get most searched keywords
        search_keywords = (
            SearchHistory.objects
            .filter(customer=customer)
            .values('keyword')
            .annotate(freq=Count('id'))
            .order_by('-freq')
        )
        top_keywords = [entry['keyword'].lower() for entry in search_keywords]

        # 3. Get most booked expert IDs
        booked_expert_ids = (
            Booking.objects
            .filter(customer=customer)
            .values('expert')
            .annotate(freq=Count('id'))
            .order_by('-freq')
        )
        booked_expert_ids = [entry['expert'] for entry in booked_expert_ids]

        # 4. Start with experts in same city
        city_experts = Expert.objects.filter(city__iexact=customer.city)

        # 5. Filter manually by matching keyword in service_categories (case-insensitive)
        matching_experts = []
        for expert in city_experts:
            if not expert.service_categories:
                continue
            if any(keyword.lower() in [cat.lower() for cat in expert.service_categories] for keyword in top_keywords):
                matching_experts.append(expert)

        # 6. Filter by distance within 10km
        nearby_experts = []
        for expert in matching_experts:
            if expert.latitude and expert.longitude:
                dist = calculate_distance(user_lat, user_lon, float(expert.latitude), float(expert.longitude))
                if dist <= 10000:
                    expert.distance = dist
                    nearby_experts.append(expert)

        # 7. Sort: booked experts first, then by rating
        sorted_experts = sorted(
            nearby_experts,
            key=lambda e: (
                -1 if e.id in booked_expert_ids else 0,
                -float(e.ratings_average or 0)
            )
        )

        # 8. Limit to top 5
        top_experts = sorted_experts[:5]

        # 9. Serialize and return
        serializer = ExpertRecommendationSerializer(top_experts, many=True)
        return Response({
            "message": "Recommended experts based on your searches and bookings",
            "search_keywords_used": top_keywords,
            "recommended_experts": serializer.data
        }, status=status.HTTP_200_OK)

