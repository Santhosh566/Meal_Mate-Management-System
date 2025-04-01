from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Registration
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Registration, Category, FoodItem, Order, OrderItem, Feedback
from decimal import Decimal
from django.db import transaction

def index(request):
    return render(request, 'Food_App/index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Check for built-in admin credentials
        if username == "admin" and password == "admin":
            request.session['user_id'] = 'admin'
            request.session['username'] = 'admin'
            request.session['user_type'] = 'admin'
            return redirect('admin_home')
        
        # Check for regular registered users
        try:
            user = Registration.objects.get(username=username)
            if check_password(password, user.password):
                # Store user info in session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['user_type'] = 'customer'
                return redirect('customer_home')
            else:
                messages.error(request, 'Invalid password!')
        except Registration.DoesNotExist:
            messages.error(request, 'Username not found!')
        
        return redirect('login')
    
    return render(request, 'Food_App/login.html')

def admin_home(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
        
    # Get total number of users (excluding admin user)
    total_users = Registration.objects.exclude(username='admin').count()
    
    context = {
        'total_users': total_users,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/admin_home.html', context)

def customer_home(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get selected category from URL parameter
    category_id = request.GET.get('category')
    
    # Get all categories
    categories = Category.objects.all()
    
    # Filter food items by category if selected
    if category_id:
        food_items = FoodItem.objects.filter(category_id=category_id)
    else:
        food_items = FoodItem.objects.all()
    
    context = {
        'categories': categories,
        'food_items': food_items,
        'selected_category': category_id,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/customer_home.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Check if passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        # Check if username exists
        if Registration.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        # Check if email exists
        if Registration.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register')

        try:
            # Create new registration
            registration = Registration(
                username=username,
                email=email,
                phone_number=phone_number,
                password=make_password(password1)  # Hash the password
            )
            registration.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('register')

    return render(request, 'Food_App/register.html')


def logout_view(request):
    # Clear all session data
    request.session.flush()
    return redirect('login')


# Category Management
def manage_categories(request):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        
        # Create new category
        Category.objects.create(name=category_name)
        messages.success(request, 'Category added successfully!')
        return redirect('manage_categories')
    
    categories = Category.objects.all().order_by('name')
    return render(request, 'Food_App/manage_categories.html', {'categories': categories})

def edit_category(request, category_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
        
    if request.method == 'POST':
        try:
            category = get_object_or_404(Category, id=category_id)
            category.name = request.POST.get('category_name')
            category.save()
            messages.success(request, 'Category updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
    
    return redirect('manage_categories')

def delete_category(request, category_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
        
    if request.method == 'POST':
        try:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
    
    return redirect('manage_categories')

# Food Items Management
def manage_food_items(request):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('food_name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        # Create new food item
        FoodItem.objects.create(
            name=name,
            category_id=category_id,
            price=price,
            description=description,
            image=image
        )
        messages.success(request, 'Food item added successfully!')
        return redirect('manage_food_items')
    
    categories = Category.objects.all()
    food_items = FoodItem.objects.all().order_by('category', 'name')
    return render(request, 'Food_App/manage_food_items.html', {
        'categories': categories,
        'food_items': food_items
    })

def delete_food_item(request, item_id):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    food_item = get_object_or_404(FoodItem, id=item_id)
    food_item.delete()
    messages.success(request, 'Food item deleted successfully!')
    return redirect('manage_food_items')

def edit_food_item(request, item_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
        
    food_item = get_object_or_404(FoodItem, id=item_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        
        # Update food item
        food_item.name = name
        food_item.description = description
        food_item.price = price
        food_item.category_id = category_id
        
        # Handle image update if provided
        if request.FILES.get('image'):
            food_item.image = request.FILES['image']
            
        food_item.save()
        messages.success(request, 'Food item updated successfully!')
        return redirect('manage_food_items')
        
    context = {
        'food_item': food_item,
        'categories': categories
    }
    return render(request, 'Food_App/edit_food_item.html', context)

# Order Management
def manage_orders(request):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'Food_App/manage_orders.html', {'orders': orders})

def update_order_status(request, order_id):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        messages.success(request, f'Order #{order_id} status updated to {new_status}')
    return redirect('manage_orders')

# User Management
def manage_users(request):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    # Get all users except the admin user
    users = Registration.objects.exclude(username='admin').order_by('-created_at')
    return render(request, 'Food_App/manage_users.html', {'users': users})

def view_user_details(request, user_id):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=user_id)
    # Get user's orders
    orders = Order.objects.filter(customer=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders,
        'total_orders': orders.count()
    }
    return render(request, 'Food_App/user_details.html', context)

def block_user(request, user_id):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.username} has been blocked!')
    return redirect('manage_users')

def unblock_user(request, user_id):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been unblocked!')
    return redirect('manage_users')

def delete_user(request, user_id):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=user_id)
    user.delete()
    messages.success(request, f'User {user.username} has been deleted!')
    return redirect('manage_users')

def add_to_cart(request, item_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    food_item = get_object_or_404(FoodItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    # Add or update item in cart
    cart = request.session['cart']
    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] += quantity
    else:
        cart[str(item_id)] = {
            'quantity': quantity,
            'price': str(food_item.price)
        }
    
    request.session.modified = True
    messages.success(request, 'Item added to cart!')
    return redirect('customer_home')

def view_cart(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for item_id, item_data in cart.items():
        food_item = FoodItem.objects.get(id=item_id)
        subtotal = float(item_data['price']) * item_data['quantity']
        cart_items.append({
            'food_item': food_item,
            'quantity': item_data['quantity'],
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'Food_App/cart.html', {
        'cart_items': cart_items,
        'total': total
    })
    
def my_orders(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get user's orders
    orders = Order.objects.filter(
        customer_id=request.session.get('user_id')
    ).order_by('-created_at')
    
    context = {
        'orders': orders,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/my_orders.html', context)

def customer_orders(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get all orders for the current customer
    orders = Order.objects.filter(
        customer_id=request.session['user_id']
    ).order_by('-created_at')
    
    # Get order items for each order
    for order in orders:
        order.items = OrderItem.objects.filter(order=order)
    
    context = {
        'orders': orders,
        'username': request.session.get('username')
    }
    
    return render(request, 'Food_App/customer_orders.html', context)

def update_cart(request, item_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        if str(item_id) in cart:
            if quantity > 0:
                cart[str(item_id)]['quantity'] = quantity
            else:
                del cart[str(item_id)]
            
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Cart updated successfully!')
    
    return redirect('view_cart')

def remove_from_cart(request, item_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Item removed from cart!')
    
    return redirect('view_cart')

def checkout(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            messages.error(request, 'Your cart is empty!')
            return redirect('view_cart')
            
        try:
            with transaction.atomic():  # Use transaction to ensure all or nothing
                # Calculate total amount
                total_amount = Decimal('0.00')
                for item_id, item_data in cart.items():
                    food_item = FoodItem.objects.get(id=item_id)
                    quantity = item_data.get('quantity', 1)
                    item_total = Decimal(str(food_item.price)) * Decimal(str(quantity))
                    total_amount += item_total

                # Create the main order
                order = Order.objects.create(
                    customer_id=request.session['user_id'],
                    total_amount=total_amount,
                    status='pending'
                )

                # Create OrderItems for each cart item
                for item_id, item_data in cart.items():
                    food_item = FoodItem.objects.get(id=item_id)
                    quantity = item_data.get('quantity', 1)
                    price = food_item.price
                    
                    OrderItem.objects.create(
                        order=order,
                        food_item=food_item,
                        quantity=quantity,
                        price=price
                    )
            
            # Redirect to payment page instead of clearing cart
            return redirect('process_payment', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('view_cart')
    
    return redirect('view_cart')

def cart_update(request, item_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        if str(item_id) in cart:
            if quantity > 0:
                cart[str(item_id)]['quantity'] = quantity
            else:
                del cart[str(item_id)]
            
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Cart updated successfully!')
    
    return redirect('view_cart')

def cart_remove(request, item_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, 'Item removed from cart!')
    
    return redirect('view_cart')

def order_confirmation(request, order_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get the order and its items
    order = get_object_or_404(Order, id=order_id, customer_id=request.session['user_id'])
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/order_confirmation.html', context)

def process_payment(request, order_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get the order
    order = get_object_or_404(Order, id=order_id, customer_id=request.session['user_id'])
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        try:
            # Update order based on payment method
            if payment_method == 'cash':
                order.payment_method = 'cash_on_delivery'
                order.payment_status = 'pending'
                order.status = 'confirmed'
                messages.success(request, 'Order confirmed! Pay on delivery.')
            
            elif payment_method == 'card':
                # Here you would normally integrate with a payment gateway
                order.payment_method = 'card'
                order.payment_status = 'paid'
                order.status = 'confirmed'
                messages.success(request, 'Payment successful!')
            
            elif payment_method == 'upi':
                # Here you would normally integrate with UPI
                order.payment_method = 'upi'
                order.payment_status = 'paid'
                order.status = 'confirmed'
                messages.success(request, 'Payment successful!')
            
            order.save()
            return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')
            return redirect('payment', order_id=order.id)
    
    # For GET request, show payment page
    context = {
        'order': order,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/payment.html', context)

def view_order_details(request, order_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
        
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/order_details.html', context)

def update_order_status(request, order_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
        
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'confirmed', 'delivered', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
            
    return redirect('manage_orders')

def customer_dashboard(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=request.session['user_id'])
    recent_orders = Order.objects.filter(customer=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'recent_orders': recent_orders,
        'favorite_items': [],  # Implement favorites functionality
    }
    return render(request, 'Food_App/customer_dashboard.html', context)

def edit_profile(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=request.session['user_id'])
    
    if request.method == 'POST':
        try:
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            
            # Add password change if provided
            new_password = request.POST.get('new_password')
            if new_password:
                user.password = make_password(new_password)
                
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('customer_dashboard')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'Food_App/edit_profile.html', {'user': user})

def order_history(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    user = get_object_or_404(Registration, id=request.session['user_id'])
    orders = Order.objects.filter(customer=user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'user': user,
    }
    return render(request, 'Food_App/order_history.html', context)

def menu(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get all categories and food items
    categories = Category.objects.all()
    food_items = FoodItem.objects.all()
    
    context = {
        'categories': categories,
        'food_items': food_items,
        'username': request.session.get('username')
    }
    return render(request, 'Food_App/menu.html', context)
from django.db.models import Avg  
def my_feedbacks(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    # Get all feedbacks for the current user
    feedbacks = Feedback.objects.filter(
        user_id=request.session['user_id']
    ).order_by('-created_at')
    
    context = {
        'feedbacks': feedbacks
    }
    return render(request, 'Food_App/my_feedbacks.html', context)

def admin_feedbacks(request):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    # Get all feedbacks for admin view
    feedbacks = Feedback.objects.all().order_by('-created_at')
    
    context = {
        'feedbacks': feedbacks
    }
    return render(request, 'Food_App/admin_feedbacks.html', context)

def submit_feedback(request, order_id):
    if not request.session.get('user_id'):
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        
        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            
            # Create feedback for each item in the order
            for order_item in order_items:
                Feedback.objects.create(
                    user_id=request.session['user_id'],
                    food_item=order_item.food_item,
                    order=order,
                    rating=rating,
                    comment=comment
                )
            
            messages.success(request, 'Thank you for your feedback!')
            return redirect('my_orders')
        
        context = {
            'order': order,
            'order_items': order_items
        }
        return render(request, 'Food_App/feedback_form.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found!')
        return redirect('my_orders')

def view_admin_feedbacks(request):
    if not request.session.get('user_id') or request.session.get('user_type') != 'admin':
        messages.error(request, 'Please login as admin!')
        return redirect('login')
    
    feedbacks = Feedback.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_feedbacks = feedbacks.count()
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'feedbacks': feedbacks,
        'total_feedbacks': total_feedbacks,
        'avg_rating': round(avg_rating, 1)
    }
    return render(request, 'Food_App/admin_view_feedbacks.html', context)
