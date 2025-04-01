from django.contrib import admin
from .models import Registration, Category, FoodItem, Order, Favorite
# Register your models here.
admin.site.register(Registration)
admin.site.register(Category)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(Favorite)
