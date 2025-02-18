from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView
from django.views.generic import TemplateView

urlpatterns = [

    path('query_ollama/', views.query_ollama, name='query_ollama'),

    path('', views.welcome, name='welcome'),
    path('accounts/', include('allauth.urls')),  


    #Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('mfa/approve/<str:token>/', views.mfa_approve, name='mfa_approve'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('check_email_exists/', views.check_email_exists, name='check_email_exists'),


    # # Change Password
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('password-change/done/', TemplateView.as_view(template_name='product/password_change_done.html'), name='password_change_done'),


    #accounts URLs
    path('account/', views.account, name='account'),

    #Profile URLs
    path('account/profile/', views.profile, name='profile'),
    path('account/profile/update/', views.update_profile, name='update_profile'),

    
    # Product URLs
    path('product/', views.product_listing, name='product_listing'),
    path('product/<slug:product_slug>/', views.product_details, name='product_detail'),
    path('product/<slug:product_slug>/update/', views.update_product, name='product_update'),
    path('add-product/', views.add_product, name='add_product'),
    path('product/<slug:slug>/delete-product/', views.delete_product, name='delete_product'),


    # Wishlist URLs
    path('product/add_to_wishlist/<slug:product_slug>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist-list/', views.wishlist_list, name='wishlist_list'),
    path('product/wishlist/remove/<slug:item_slug>/', views.remove_wishlist_item, name='remove_wishlist_item'),
    path('wishlist/remove/<slug:item_slug>/', views.remove_from_wishlist, name='remove_from_wishlist'),


    
    # Review URLs
    path('product/<slug:product_slug>/add-review/', views.add_review, name='add_review'),
    path('product/<slug:product_slug>/delete-review/', views.delete_review, name='delete_review'),
    path('product/<slug:product_slug>/update-review/', views.update_review, name='update_review'),


    #Reset Password URLs
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='product/password_reset_done.html'
    ), name='password_reset_done'), 
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='product/password_reset_complete.html'),
        name='password_reset_complete'
    ),

    # User's Listing
    path('users/', views.users_listing, name='user_listing'),


    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('product/<slug:product_slug>/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('<slug:item_slug>/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('product/<slug:item_slug>/cart/remove/', views.remove_cart_item, name='remove_cart_item'),
    path('product/<slug:item_slug>/cart/update/', views.update_cart, name='update_cart'),


    # Addresses URLs
    path('addresses/', views.manage_address, name='addresses'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/set-default/<str:encrypted_address>/', views.set_default_address, name='set_default_address'),
    path('addresses/edit/<str:encrypted_address>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<str:encrypted_address>/', views.delete_address, name='delete_address'),

    path('addresses/reviews-list/', views.reviews_list, name='reviews_list'),
]