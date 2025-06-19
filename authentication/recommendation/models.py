from django.db import models

# Create your models here.
from django.db import models
from user_signup.models import Customer  # Adjust path based on your project structure

class SearchHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='search_history')
    keyword = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.email} searched '{self.keyword}'"