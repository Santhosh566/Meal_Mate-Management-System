from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('customer_home/', views.customer_home, name='customer_home'),
    path('logout/', views.logout_view, name='logout'),
     path('my-orders/', views.my_orders, name='my_orders'),  # Make sure this exact line exists
    path('admin_home/categories/', views.manage_categories, name='manage_categories'),
    path('admin_home/category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    

    # Food Items Management URLs
    path('admin_home/food-items/', views.manage_food_items, name='manage_food_items'),
    path('admin_home/food-items/edit/<int:item_id>/', views.edit_food_item, name='edit_food_item'),
    path('admin_home/food-item/delete/<int:item_id>/', views.delete_food_item, name='delete_food_item'),
    

    # Order Management URLs
    path('admin_home/orders/', views.manage_orders, name='manage_orders'),
    path('admin_home/order/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    

    # User Management URLs
    path('admin_home/users/', views.manage_users, name='manage_users'),
    path('admin_home/user/block/<int:user_id>/', views.block_user, name='block_user'),
    # User Management URLs
path('admin_home/users/', views.manage_users, name='manage_users'),
path('admin_home/users/view/<int:user_id>/', views.view_user_details, name='view_user_details'),
path('admin_home/users/block/<int:user_id>/', views.block_user, name='block_user'),
path('admin_home/users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
path('admin_home/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

# Customer URLs
path('customer_home/', views.customer_home, name='customer_home'),
path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.view_cart, name='view_cart'),
path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
path('cart/checkout/', views.checkout, name='checkout'),
path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
path('my-orders/', views.customer_orders, name='customer_orders'),  # Add this line
path('order/<int:order_id>/details/', views.view_order_details, name='view_order_details'),
path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
path('admin_home/categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
path('admin_home/categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
path('customer_home/dashboard/', views.customer_dashboard, name='customer_dashboard'),
path('customer_home/profile/edit/', views.edit_profile, name='edit_profile'),
path('customer_home/orders/', views.order_history, name='order_history'),

path('customer_home/menu/', views.menu, name='menu'),
path('my-feedbacks/', views.my_feedbacks, name='my_feedbacks'),
path('admin_home/feedbacks/', views.admin_feedbacks, name='admin_feedbacks'),
path('submit_feedback/<int:order_id>/', views.submit_feedback, name='submit_feedback'),
path('admin_home/view-feedbacks/', views.view_admin_feedbacks, name='view_admin_feedbacks'),



]
