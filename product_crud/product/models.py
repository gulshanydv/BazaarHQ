from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not getattr(instance, '_profile_created', False) and not instance.is_superuser:
        UserProfile.objects.get_or_create(user=instance)



@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()



class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, help_text='Quantity of this product in stock')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text='Discount percentage')
    image = models.ImageField(upload_to='product_image/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Create a slug from the name
        super().save(*args, **kwargs)

    def discounted_price(self):
        """Calculate and return the discounted price, rounded to two decimal places"""
        discounted_price = self.price * (1 - (self.discount / 100))
        return round(discounted_price, 2)

    def __str__(self):
        return self.name



# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    email = models.EmailField(unique=True, null=True)  

    wishlist = models.ManyToManyField(Product, blank=True, related_name='wishlist_users')  
    cart = models.ManyToManyField(Product, blank=True, related_name='cart_users') 

    
    def __str__(self):
        return self.user.username
    

# Monkey patch User model to include `profile`
def get_user_profile(self):
    return self.userprofile

User.add_to_class('profile', property(get_user_profile))






class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.product.discounted_price()*item.quantity for item in self.item.all())
    
    def __str__(self):
        return f"wishlist for {self.user.username}"
    



class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True)  # Ensure this exists
    
    def save(self, *args, **kwargs):
        if not self.slug and self.product.name:
            self.slug = slugify(self.product.name)  # Create a slug from the product name
        super().save(*args, **kwargs)
    



class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def total_price(self):
        return sum(item.product.discounted_price()*item.quantity for item in self.item.all())




class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    slug = models.SlugField(blank=True, null=True)

    def subtotal(self):
        return self.product.discounted_price() * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug and self.product.name:
            self.slug = slugify(self.product.name)  # Create a slug from the product name
        super().save(*args, **kwargs)
    

    

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"



class Address(models.Model):
    HOME = 'home'
    WORK = 'work'

    ADDRESS_TYPES = [
        (HOME, 'Home'),
        (WORK, 'Work'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    alt_phone_number = models.CharField(max_length=20, blank=True, null=True)
    pincode = models.CharField(max_length=6)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    house_no_or_building_name = models.CharField(max_length=255)
    area_or_colony = models.CharField(max_length=255)
    nearby_landmark = models.CharField(max_length=255, blank=True, null=True)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default=HOME)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.address_type} address"
    
    def set_default(self):  
        Address.objects.filter(user=self.user).update(is_default=False)
        self.is_default = True
        self.save()





