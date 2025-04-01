from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Registration(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='food_images/')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('cash_on_delivery', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI Payment'),
    )
    
    customer = models.ForeignKey('Registration', on_delete=models.CASCADE)  # Link to your Registration model
    items = models.ManyToManyField(FoodItem, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name} in Order #{self.order.id}"

class Rating(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    customer = models.ForeignKey(Registration, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1,1), (2,2), (3,3), (4,4), (5,5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure one rating per customer per food item
        unique_together = ('food_item', 'customer')
class Favorite(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'food_item')

class Feedback(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    user = models.ForeignKey('Registration', on_delete=models.CASCADE)
    food_item = models.ForeignKey('FoodItem', on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        # Ensure one feedback per food item per order
        unique_together = ['user', 'food_item', 'order']
    
    def __str__(self):
        return f"Feedback by {self.user.username} for {self.food_item.name} (Order #{self.order.id})"
    
    @property
    def rating_stars(self):
        """Returns star representation of rating"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def is_positive(self):
        """Returns True if rating is 4 or above"""
        return self.rating >= 4

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)
    discount_percentage = models.IntegerField(
        default=0,
        help_text="Discount percentage (0-100)"
    )
    minimum_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Minimum order amount required"
    )
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_uses = models.IntegerField(default=0, help_text="0 for unlimited uses")
    times_used = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"
    
    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False
        return self.valid_from <= now <= self.valid_to
