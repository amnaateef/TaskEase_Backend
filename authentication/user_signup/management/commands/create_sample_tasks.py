from django.core.management.base import BaseCommand
from user_signup.models import Task, Expert, Customer
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Creates sample tasks with prices for testing'

    def handle(self, *args, **kwargs):
        # Sample task data
        sample_tasks = [
            {
                'title': 'Plumbing Repair',
                'description': 'Fix leaking pipe in bathroom',
                'category': 'Plumbing',
                'price': Decimal('2500.00')
            },
            {
                'title': 'Electrical Installation',
                'description': 'Install new ceiling fan',
                'category': 'Electrical',
                'price': Decimal('3500.00')
            },
            {
                'title': 'Carpentry Work',
                'description': 'Build custom bookshelf',
                'category': 'Carpentry',
                'price': Decimal('5000.00')
            },
            {
                'title': 'Painting Service',
                'description': 'Paint living room walls',
                'category': 'Painting',
                'price': Decimal('8000.00')
            },
            {
                'title': 'AC Repair',
                'description': 'Fix AC not cooling',
                'category': 'HVAC',
                'price': Decimal('4500.00')
            }
        ]

        # Get or create a sample expert
        expert, _ = Expert.objects.get_or_create(
            email='expert@example.com',
            defaults={
                'firstname': 'John',
                'lastname': 'Doe',
                'phone_number': '03001234567',
                'city': 'Karachi',
                'role': 'Expert',
                'years_of_experience': 5,
                'service_categories': ['Plumbing', 'Electrical', 'Carpentry', 'Painting', 'HVAC']
            }
        )

        # Get or create a sample customer
        customer, _ = Customer.objects.get_or_create(
            email='customer@example.com',
            defaults={
                'firstname': 'Jane',
                'lastname': 'Smith',
                'phone_number': '03001234568',
                'city': 'Karachi',
                'role': 'Customer'
            }
        )

        # Create tasks
        tasks_created = 0
        for task_data in sample_tasks:
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                expert=expert,
                customer=customer,
                defaults={
                    'description': task_data['description'],
                    'category': task_data['category'],
                    'price': task_data['price'],
                    'status': random.choice(['pending', 'in_progress', 'completed'])
                }
            )
            if created:
                tasks_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {tasks_created} sample tasks')
        ) 