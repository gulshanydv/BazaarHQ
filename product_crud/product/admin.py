from django.contrib import admin
from .models import UserProfile, Product, Wishlist, WishlistItem, Review, Cart, CartItem


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'discounted_price', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at', 'discount')

