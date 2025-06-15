from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from user_signup.models import Expert
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample experts with location data'

    def handle(self, *args, **kwargs):
        # Sample data for experts
        experts_data = [
            {
                'email': 'expert1@example.com',
                'password': 'testpass123',
                'firstname': 'John',
                'lastname': 'Smith',
                'cnic': '12345-6789012-3',
                'gender': 'Male',
                'phone_number': '03001234567',
                'city': 'Islamabad',
                'latitude': 33.6844,
                'longitude': 73.0479,
                'service_categories': ['Plumbing', 'Electrical'],
                'years_of_experience': 5,
                'bio': 'Experienced plumber and electrician',
                'verified_status': True
            },
            {
                'email': 'expert2@example.com',
                'password': 'testpass123',
                'firstname': 'Sarah',
                'lastname': 'Johnson',
                'cnic': '12345-6789012-4',
                'gender': 'Female',
                'phone_number': '03001234568',
                'city': 'Rawalpindi',
                'latitude': 33.5651,
                'longitude': 73.0169,
                'service_categories': ['Carpentry', 'Painting'],
                'years_of_experience': 3,
                'bio': 'Professional carpenter and painter',
                'verified_status': True
            },
            {
                'email': 'expert3@example.com',
                'password': 'testpass123',
                'firstname': 'Ahmed',
                'lastname': 'Khan',
                'cnic': '12345-6789012-5',
                'gender': 'Male',
                'phone_number': '03001234569',
                'city': 'Lahore',
                'latitude': 31.5204,
                'longitude': 74.3587,
                'service_categories': ['HVAC', 'Plumbing'],
                'years_of_experience': 7,
                'bio': 'HVAC specialist with plumbing expertise',
                'verified_status': True
            },
            {
                'email': 'expert4@example.com',
                'password': 'testpass123',
                'firstname': 'Fatima',
                'lastname': 'Ali',
                'cnic': '12345-6789012-6',
                'gender': 'Female',
                'phone_number': '03001234570',
                'city': 'Karachi',
                'latitude': 24.8607,
                'longitude': 67.0011,
                'service_categories': ['Electrical', 'HVAC'],
                'years_of_experience': 4,
                'bio': 'Electrical engineer and HVAC specialist',
                'verified_status': True
            },
            {
                'email': 'expert5@example.com',
                'password': 'testpass123',
                'firstname': 'Usman',
                'lastname': 'Raza',
                'cnic': '12345-6789012-7',
                'gender': 'Male',
                'phone_number': '03001234571',
                'city': 'Peshawar',
                'latitude': 34.0150,
                'longitude': 71.5249,
                'service_categories': ['Carpentry', 'Plumbing'],
                'years_of_experience': 6,
                'bio': 'Skilled carpenter and plumber',
                'verified_status': True
            }
        ]

        for expert_data in experts_data:
            # Create User instance
            user = User.objects.create_user(
                username=expert_data['email'],
                email=expert_data['email'],
                password=expert_data['password'],
                first_name=expert_data['firstname'],
                last_name=expert_data['lastname'],
                role='Expert',
                cnic=expert_data['cnic'],
                gender=expert_data['gender'],
                phone_number=expert_data['phone_number'],
                city=expert_data['city'],
                latitude=expert_data['latitude'],
                longitude=expert_data['longitude']
            )

            # Create Expert instance
            Expert.objects.create(
                email=expert_data['email'],
                password=expert_data['password'],
                firstname=expert_data['firstname'],
                lastname=expert_data['lastname'],
                cnic=expert_data['cnic'],
                gender=expert_data['gender'],
                service_categories=expert_data['service_categories'],
                years_of_experience=expert_data['years_of_experience'],
                phone_number=expert_data['phone_number'],
                city=expert_data['city'],
                latitude=expert_data['latitude'],
                longitude=expert_data['longitude'],
                bio=expert_data['bio'],
                verified_status=expert_data['verified_status']
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample experts')) 