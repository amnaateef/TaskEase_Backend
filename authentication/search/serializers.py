from django.db import models

# Create your models here.
from rest_framework import serializers
from user_signup.models import Expert
from user_signup.models import Service

class ExpertSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = [
            'id', 'full_name', 'profile_picture', 'city', 'service_categories',
            'starting_price', 'ratings_average', 'total_reviews',
            'years_of_experience', 'availability', 'latitude', 'longitude',
            'bio', 'verified_status',
        ]

    def get_full_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"

class ServiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
