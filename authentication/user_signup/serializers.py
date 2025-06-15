from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Expert, Customer, Task
import random
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=['Expert', 'Customer'], required=True)
    cnic = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role', 
                 'phone_number', 'city', 'latitude', 'longitude', 'cnic', 'gender')
        read_only_fields = ('id',)

    def create(self, validated_data):
        # Generate username from email (everything before @)
        email = validated_data.get('email')
        validated_data['username'] = email.split('@')[0]
        
        # Hash the password
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        user = authenticate(email=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # Create JWT token
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "role": user.role,
        }

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['role'] = self.user.role
        return data

def validate_latitude(value):
    str_val = str(value).replace('.', '').replace('-', '')
    if len(str_val) > 10:
        raise serializers.ValidationError("Latitude must be 10 digits or fewer in total.")
    return value    

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords don't match."})
        
        if len(attrs['new_password']) < 8:
            raise serializers.ValidationError({"new_password": "Password must be at least 8 characters long."})
        
        return attrs    

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                 'address', 'city', 'bio', 'profile_picture', 'latitude', 'longitude')
        read_only_fields = ('id', 'role', 'cnic', 'gender')  # These fields cannot be updated

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone_number(self, value):
        if value and len(value) > 15:
            raise serializers.ValidationError("Phone number must be 15 digits or fewer.")
        return value

    def validate_latitude(self, value):
        if value is not None:
            if value < -90 or value > 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_longitude(self, value):
        if value is not None:
            if value < -180 or value > 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value

class ProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 
                 'address', 'city', 'bio', 'profile_picture', 'role', 'cnic', 
                 'gender', 'latitude', 'longitude')
        read_only_fields = fields  # All fields are read-only for GET requests    

class NearbyExpertSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = ('id', 'full_name', 'task_count', 'rating', 'distance', 
                 'city', 'service_categories', 'years_of_experience', 
                 'profile_picture', 'verified_status')

    def get_task_count(self, obj):
        return Task.objects.filter(expert=obj).count()

    def get_rating(self, obj):
        return float(obj.ratings_average) if obj.ratings_average else 0.0

    def get_distance(self, obj):
        return getattr(obj, 'distance', 0)

    def get_full_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"

class ExpertTaskSerializer(serializers.ModelSerializer):
    expert_details = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'expert_details', 'status', 
                 'created_at', 'updated_at', 'price', 'category', 'picture')

    def get_expert_details(self, obj):
        try:
            expert = obj.expert
            return {
                'id': expert.id,
                'name': f"{expert.firstname} {expert.lastname}",
                'email': expert.email,
                'phone_number': expert.phone_number,
                'city': expert.city,
                'rating': round(random.uniform(2.0, 4.9), 1)  # Random rating for now
            }
        except Exception as e:
            logger.error(f"Error getting expert details: {str(e)}")
            return {
                'id': None,
                'name': 'Unknown Expert',
                'email': None,
                'phone_number': None,
                'city': None,
                'rating': 0.0
            }

class ExpertTaskListSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Task
        fields = ('id', 'title', 'category', 'picture', 'price')

class ExpertWithTasksSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()
    years_of_experience = serializers.IntegerField()

    class Meta:
        model = Expert
        fields = ('id', 'firstname', 'lastname', 'tasks', 'total_tasks', 'years_of_experience')

    def get_tasks(self, obj):
        tasks = Task.objects.filter(expert=obj)
        return ExpertTaskListSerializer(tasks, many=True).data

    def get_total_tasks(self, obj):
        return Task.objects.filter(expert=obj).count()    