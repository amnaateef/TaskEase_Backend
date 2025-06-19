from rest_framework import serializers
from .models import SearchHistory
from user_signup.models import Expert

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'



class ExpertRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = [
            'id', 'firstname', 'lastname', 'email', 'city', 'service_categories',
            'ratings_average', 'starting_price', 'profile_picture'
        ]        