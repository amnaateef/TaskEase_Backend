from django.contrib import admin

# Register your models here.
from .models import Expert, Customer,Booking,RatingHistory,Review,Payment,Service,WorkImage

admin.site.register(Expert)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(RatingHistory)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Service)
admin.site.register(WorkImage)