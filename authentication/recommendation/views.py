from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from user_signup.models import Customer, Expert,Booking,Service,Payment
from .models import SearchHistory
from user_signup.serializers import NearbyExpertSerializer
from search.views import calculate_distance  # reuse your existing distance function
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ExpertRecommendationSerializer
from django.db.models import Count, Avg, Q
from sklearn.feature_extraction.text import TfidfVectorizer
from math import radians, sin, cos, sqrt, atan2
import numpy as np


'''class ExpertRecommendationView(APIView):
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
'''

'''class MLRecommendedServicesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get(self, request):
        user = request.user
        if user.role != 'Customer':
            return Response({'error': 'Only customers can access this endpoint.'}, status=403)

        customer = Customer.objects.get(email=user.email)
        lat, lon = customer.latitude, customer.longitude

        # User’s past data
        search_terms = list(SearchHistory.objects.filter(customer=customer)
                            .values_list('keyword', flat=True))
        booked_tasks = Task.objects.filter(customer=customer)
        booked_categories = list(booked_tasks.values_list('category', flat=True))
        customer_profile_text = ' '.join(search_terms + booked_categories)

        # All services in customer city
        services = Service.objects.select_related('expert').filter(expert__city=customer.city)

        service_texts = []
        service_ids = []
        expert_locations = {}
        for service in services:
            text = f"{service.selected_service} {service.description}"
            service_texts.append(text)
            service_ids.append(service.id)
            expert_locations[service.id] = (service.expert.latitude, service.expert.longitude)

        # TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(service_texts)
        customer_vector = vectorizer.transform([customer_profile_text])
        similarity_scores = np.dot(tfidf_matrix, customer_vector.T).toarray().flatten()

        # Booking popularity
        expert_booking_counts = Task.objects.values('expert').annotate(count=Count('id'))
        booking_score_map = {entry['expert']: entry['count'] for entry in expert_booking_counts}

        # Ratings
        expert_ratings = Review.objects.values('expert').annotate(avg_rating=Avg('rating'))
        rating_score_map = {entry['expert']: entry['avg_rating'] or 0 for entry in expert_ratings}

        # Score each service
        scored_services = []
        for idx, service_id in enumerate(service_ids):
            service = Service.objects.get(id=service_id)
            expert = service.expert

            # Haversine distance
            distance = self.haversine(lat, lon, expert.latitude, expert.longitude)

            if distance <= 0.5:  # Only include nearby services
                # Scores
                sim_score = similarity_scores[idx]  # 0–1
                booking_score = min(booking_score_map.get(expert.id, 0) / 10.0, 1.0)  # Normalize
                rating_score = min(rating_score_map.get(expert.id, 0) / 5.0, 1.0)  # Normalize
                proximity_score = 1.0  # since within 0.5km

                # Final weighted score
                final_score = (sim_score * 0.4) + (booking_score * 0.2) + (rating_score * 0.3) + (proximity_score * 0.1)

                scored_services.append({
                    "service": service,
                    "score": round(final_score, 3),
                    "distance": round(distance, 3)
                })

        # Sort and return top 12
        top_services = sorted(scored_services, key=lambda x: x['score'], reverse=True)[:12]

        # Format response
        response_data = []
        for item in top_services:
            service = item['service']
            expert = service.expert
            response_data.append({
                "id": service.id,
                "title": service.selected_service,
                "description": service.description,
                "price": service.price,
                "distance_km": item["distance"],
                "score": item["score"],
                "expert_name": f"{expert.firstname} {expert.lastname}",
                "expert_rating": round(rating_score_map.get(expert.id, 0), 2),
                "image": request.build_absolute_uri(service.image.url) if service.image else None
            })

        return Response(response_data, status=200)'''

class MLRecommendedServicesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get(self, request):
        user = request.user
        if user.role != 'Customer':
            return Response({"error": "Only customers can access recommendations."}, status=403)

        try:
            customer = Customer.objects.get(email=user.email)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)

        lat, lon = float(customer.latitude), float(customer.longitude)

        # Most searched keywords
        search_keywords = list(SearchHistory.objects.filter(customer=customer)
                               .values_list('keyword', flat=True))

        # Most booked services by this customer
        booked_services = Booking.objects.filter(customer=customer).values_list('task__selected_service', flat=True)

        # Most booked experts overall
        top_experts = Booking.objects.values('expert').annotate(book_count=Count('id')).order_by('-book_count')[:5]
        top_expert_ids = [e['expert'] for e in top_experts]

        # Top-rated experts (from Expert table)
        top_rated_experts = Expert.objects.order_by('-ratings_average')[:5]
        top_rated_expert_ids = [e.id for e in top_rated_experts]

        # Combine into customer profile text
        customer_profile_text = ' '.join(search_keywords) + ' ' + ' '.join(booked_services)

        # Candidate services in customer city
        services = Service.objects.select_related('expert').filter(
            city__iexact=customer.city,
            expert__city__iexact=customer.city
        )

        service_texts = []
        service_ids = []
        expert_locations = {}

        for service in services:
            text = f"{service.selected_service} {service.description}"
            service_texts.append(text)
            service_ids.append(service.id)
            expert_locations[service.id] = (float(service.expert.latitude), float(service.expert.longitude))

        if not service_texts:
            return Response([], status=200)

        # TF-IDF Similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(service_texts)
        customer_vector = vectorizer.transform([customer_profile_text])
        similarity_scores = np.dot(tfidf_matrix, customer_vector.T).toarray().flatten()

        scored_services = []
        for idx, service_id in enumerate(service_ids):
            service = Service.objects.get(id=service_id)
            expert = service.expert
            distance = self.haversine(lat, lon, float(expert.latitude), float(expert.longitude))

            if distance > 10:
                continue

            sim_score = similarity_scores[idx]
            is_top_expert = 1 if expert.id in top_expert_ids else 0
            is_top_rated = 1 if expert.id in top_rated_expert_ids else 0
            proximity_score = 1

            final_score = (sim_score * 0.5) + (is_top_expert * 0.2) + (is_top_rated * 0.2) + (proximity_score * 0.1)

            scored_services.append({
                "service": service,
                "score": round(final_score, 3),
                "distance": round(distance, 3)
            })

        top_services = sorted(scored_services, key=lambda x: x["score"], reverse=True)[:12]

        # Format response
        response = []
        for item in top_services:
            s = item["service"]
            expert = s.expert

            # Fetch work images for the service
            work_images = s.work_images.all().values_list('image', flat=True)
            work_image_paths = list(work_images)

            response.append({
                "id": s.id,
                "selected_service": s.selected_service,
                "description": s.description,
                "price": s.price,
                "distance_km": item["distance"],
                "score": item["score"],
                "expert_name": f"{expert.firstname} {expert.lastname}",
                "expert_rating": float(expert.ratings_average),
                "cover_image": s.cover_image.url if s.cover_image else None,
                "work_images": work_image_paths,
                "expert_id": expert.id,
                "city": s.city,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "expertise_level": s.expertise_level,
                "years_of_experience": s.years_of_experience,
                "client_present": s.client_present,
                "use_tools": s.use_tools,
                "trial_session": s.trial_session,
                "late_arrival": s.late_arrival,
                "same_day_cancel": s.same_day_cancel,
                "rescheduling": s.rescheduling,
                "partial_payment": s.partial_payment,
                "inspection": s.inspection,
                "currency": s.currency,
                "hourly_rate": float(s.hourly_rate),
                "weekend_rate": float(s.weekend_rate),
                "bulk_discount": float(s.bulk_discount),
                "time_slots": s.time_slots,
                "scheduled_for": s.scheduled_for,
                "created_at": s.created_at,
                "updated_at": s.updated_at
            })

        return Response(response, status=200)

