from django.db import models
from .custom_user import CustomUser

# Create your models here

class Expert(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, default="Expert")
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    cnic = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
     # 🔄 Updated field to allow multiple service categories
    service_categories = models.JSONField(null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    availability = models.TextField(null=True, blank=True)

    phone_number = models.CharField(max_length=20,null=True, blank=True)
    city = models.CharField(max_length=100,null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8,null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8,null=True, blank=True)

    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ratings_average = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    total_reviews = models.IntegerField(default=0,null=True, blank=True)
    profile_picture = models.ImageField(upload_to='experts/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    
    certifications = models.JSONField(null=True, blank=True)  
    portfolio_images = models.JSONField(null=True, blank=True)
    
    verified_status = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Customer(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, default="User")
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    cnic = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    # additional attributes for search 
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return self.email

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='tasks')
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    picture = models.ImageField(upload_to='task_pictures/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task: {self.title} by {self.customer.firstname}"


class Review(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='reviews')
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE, related_name='reviews')
    task = models.ForeignKey('user_signup.Task', on_delete=models.SET_NULL, null=True, blank=True)

    rating = models.PositiveSmallIntegerField()  # e.g., 1 to 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.firstname} on {self.expert.firstname}"

class RatingHistory(models.Model):
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rating of {self.rating} for {self.expert} on {self.created_at}"

class Booking(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='bookings')
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE, related_name='bookings')
    task = models.ForeignKey('user_signup.Task', on_delete=models.CASCADE, related_name='bookings')

    scheduled_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[('booked', 'Booked'), ('cancelled', 'Cancelled'), ('completed', 'Completed')],
        default='booked'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking: {self.customer.firstname} → {self.expert.firstname}"

class Payment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.task.title}"

