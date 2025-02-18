from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .forms import UserSignupForm, UserProfileForm, ProductForm, ProductUpdateForm, ReviewForm, UpdateReviewForm, CustomResetPasswordForm, CustomSetPasswordForm, AddressForm, CustomPasswordChangeForm
from .models import UserProfile, Product, Wishlist, WishlistItem, Review, Cart, CartItem, Address
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.cache import patch_cache_control
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from .utils import send_otp_mail
from django.http import JsonResponse
from .utils import send_otp_mail
from django.contrib.auth.models import User
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils.crypto import get_random_string
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.contrib.auth.views import PasswordChangeView
from .utils import send_sms 

#LLAMA models
import ollama
from django.http import JsonResponse

def query_ollama(request):
    user_query = request.GET.get("query", "")

    if user_query:
        try:
            system_message = {
                "role": "system", 
                "content": (
                    "You are a highly specialized assistant with expertise only in eCommerce, eCommerce products, "
                    "and electric products related to eCommerce. You are not allowed to answer any questions outside of these topics. "
                    "Under no circumstances should you provide information or engage in discussions unrelated to eCommerce, eCommerce products, "
                    "or electric products. Any queries outside these subjects should be ignored, and you should not generate responses for them. "
                    "Your response must strictly be relevant to eCommerce and electric products only. Additionally, your response should not exceed "
                    "210 words in length."
                )
            }

            # Combine the system message with the user query
            messages = [
                system_message,
                {"role": "user", "content": user_query}
            ]

            # Query the Ollama model
            response = ollama.chat(model="llama3.2:latest", messages=messages)

            # Extract the answer from the model's response
            answer = response.get('message', {}).get('content', 'No response from model')

            return JsonResponse({"response": answer})  # Send the response back

        except Exception as e:
            print(f"Error querying Ollama model: {e}")
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "No query provided"}, status=400)





def password_reset_request(request):
    if request.method == "POST":
        form = CustomResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)

            if users.exists():
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(str(user.pk).encode())
                    reset_link = f"http://{get_current_site(request).domain}/reset/{uid}/{token}/"
                    
                    subject = "Password Reset Request"
                    message = render_to_string('product/password_reset_email.html', {
                        'user': user,
                        'reset_link': reset_link,
                    })
                    send_mail(
                        subject,
                        message,
                        'your_email@example.com',  # Replace with your actual email
                        [email],
                        fail_silently=False,
                        html_message=message
                    )
                # Show success message
                messages.success(request, "Password reset link has been sent to your email.")
            else:
                messages.error(request, "No user found with that email address.")
            return render(request, 'product/password_reset_form.html', {'form': form})
    else:
        form = CustomResetPasswordForm()
    return render(request, 'product/password_reset_form.html', {'form': form})
    


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if request.method == "POST":
                form = CustomSetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your password has been successfully reset.")
                    return redirect('login')
            else:
                form = CustomSetPasswordForm(user)
            return render(request, 'product/password_reset_confirm.html', {'form':form})
        else:
            return redirect('password_reset_invalid')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return redirect('password_reset_invalid')



def welcome(request):
    return render(request, 'product/welcome.html')



def send_otp(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'})

        send_otp_mail(email)
        return JsonResponse({'success': True, 'message': 'OTP sent successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



def check_email_exists(request):
    email = request.POST.get('email')
    email_exists = User.objects.filter(email=email).exists()
    return JsonResponse({'email_exists': email_exists})



def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            otp = form.cleaned_data.get('otp')

            # Validate OTP
            cached_otp = cache.get(f'otp_{email}')

            if cached_otp == otp:
                user = form.save(commit=False)
                user.email = email
                user._profile_created = True
                user.save()
               
                 # Create UserProfile instance
                try:
                    user_profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'first_name': form.cleaned_data.get('first_name'),
                            'last_name': form.cleaned_data.get('last_name'),
                            'mobile_no': form.cleaned_data.get('mobile_no'),
                            'address': form.cleaned_data.get('address'),
                            'profile_pic': form.cleaned_data.get('profile_pic'),
                            'email': email,
                        }
                    )
                    if not created:
                        # Update existing profile
                        user_profile.first_name = form.cleaned_data.get('first_name')
                        user_profile.last_name = form.cleaned_data.get('last_name')
                        user_profile.mobile_no = form.cleaned_data.get('mobile_no')
                        user_profile.address = form.cleaned_data.get('address')
                        user_profile.profile_pic = form.cleaned_data.get('profile_pic')
                        user_profile.email = email
                        user_profile.save()

                except IntegrityError:
                    messages.error(request, "A profile for this user already exists. Please contact support.")
                    return redirect('signup')


                cache.delete(f'otp_{email}')

                messages.success(request, 'Signup successful!')

                return redirect('login')

            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
                return redirect('signup')
               
        else:
            messages.error(request, "Please fix the errors in the form.")
            
    else:
        form = UserSignupForm()
    return render(request, 'product/signup.html', {'form': form})


mfa_tokens = {}

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            # Check if the user is logging in with an email or username
            username = request.POST['username']
            password = request.POST['password']
          
            user = authenticate(
                request,
                username=username,
                password=password,
                backend='django.contrib.auth.backends.ModelBackend'  # Specify the backend here
            )
            
            if user is not None:
                # Generate token
                token = get_random_string(length=32)
                mfa_tokens[token] = user.username

                # Send the email with the token link
                mfa_link = request.build_absolute_uri(
                    reverse('mfa_approve', args=[token])
                )
                send_mail(
                    'Approve your login',
                    f"""
                    <html>
                    <body>
                        <p>Click the below button to approve your login:</p>
                        <a href="{mfa_link}" style="display: inline-block; background-color: #007BFF; color: white; padding: 10px 20px; text-align: center; text-decoration: none; border-radius: 5px;">Approve Login</a>
                    </body>
                    </html>
                    """,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=f"""
                    <html>
                    <body>
                        <p>Click the below button to approve your login:</p>
                        <a href="{mfa_link}" style="display: inline-block; background-color: #007BFF; color: white; padding: 10px 20px; text-align: center; text-decoration: none; border-radius: 5px;">Approve Login</a>
                    </body>
                    </html>
                    """
                )
                # Add a success message
                messages.success(request, 'An approval email has been sent. Please check your inbox to approve your login.')

            else:
                # Add an error message if credentials are invalid
                messages.error(request, 'Invalid username or password.')

        else:
            # Add an error message if the form is not valid
            messages.error(request, 'Invalid username or password.')

    else:
        form = AuthenticationForm()
    
    # Render the login page with any potential messages
    return render(request, 'product/login.html', {'form': form})




def mfa_approve(request, token):
    if token in mfa_tokens:
        username = mfa_tokens.pop(token)
        user = get_user_model()
        try:
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('product_listing')
        except User.DoesNotExist:
            return HttpResponse('Invalid or expire token.')
    return HttpResponse('Invalid or expire token.')




@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    response = render(request, 'product/profile.html', {'profile':user_profile})
    patch_cache_control(response, no_cache=True, no_store=True, must_revalslugate=True)
    return response




@login_required
def update_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')

            # phone_number = '+91' + form.cleaned_data.get('mobile_no')
            # user_name = request.user.username
            # message = f"Dear {user_name}, your mobile number has been successfully added to your profile. If you have any questions, feel free to contact our support team."
            # send_sms(phone_number, message) 

            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'product/update_profile.html', {'form': form})



@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'product added successfully.')
            return redirect('product_listing')
    else:
        form = ProductForm()
    return render(request, 'product/add_product.html', {'form': form})



@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.delete()
    messages.success(request, f"Product {product.name} has been deleted successfully.")
    return redirect('product_listing')




def product_details(request, product_slug):
    current_user = request.user
    product = get_object_or_404(Product, slug=product_slug)
    reviews = Review.objects.filter(product=product)

    wishlist = Wishlist.objects.filter(user=request.user).first()  
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)

    if not wishlist:
        wishlist = Wishlist.objects.create(user=request.user)

    in_wishlist = wishlist.items.filter(product=product).exists()
    in_cart = cart.items.filter(product=product).exists()
    
    return render(request, 'product/product.html', 
                  {'product':product,
                   'reviews':reviews, 
                   'current_user':current_user,
                   'in_wishlist': in_wishlist, 
                   'in_cart': in_cart,
                })



@login_required
def product_listing(request):
    search = request.GET.get('search', '')
    product_name = request.GET.get('product_name','')
    min_price = request.GET.get('min_price','')
    max_price = request.GET.get('max_price','')

    # Fetch all products
    products = Product.objects.all()

    #show review 
    reviews = Review.objects.all()

    # Apply search and filters
    if search:
        products = products.filter(name__icontains=search)
    if product_name:
        products = products.filter(name__icontains=product_name)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Apply pagination
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    response = render(request, 'product/product_listing.html',{'products':products, 'reviews':reviews})
    patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)
    return response



@login_required
def update_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if not request.user.is_superuser:
        return redirect('welcome')
    
    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_detail', product_slug=product.slug)
    else:
        form = ProductUpdateForm(instance=product)
    return render(request, 'product/update_product.html', {"form": form, 'product':product})



@login_required
def add_to_wishlist(request, product_slug):
    if request.user.is_superuser:
        return HttpResponse("You cannot add items to the wishlist as a superuser.", status=403)
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return HttpResponse("Product not found.", status=400)
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    if created:
        messages.success(request, 'Your Wishlist has been created')
    else:
        messages.info(request, 'Your wishlist has been already created')

    WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

    return redirect('product_detail', product_slug=product.slug)




@login_required
def wishlist_list(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.all()
    return render(request, 'product/wishlist_listing.html', {'wishlist_items':wishlist_items})




@login_required
def remove_from_wishlist(request, item_slug):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    try:
        item = wishlist.items.get(product__slug=item_slug)
    except WishlistItem.DoesNotExist:
        messages.error(request, 'Item doesnot exist')
        return redirect('wishlist_list', ) 
    item.delete()
    messages.warning(request,'Item removed from wishlist.')
    return redirect('wishlist_list')


@login_required
def remove_wishlist_item(request, item_slug):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    try:
        item = wishlist.items.get(product__slug=item_slug)
    except WishlistItem.DoesNotExist:
        messages.error(request, 'Item doesnot exist')
        return redirect('product_detail', product_slug=item_slug)
    item.delete()
    messages.warning(request,'Item removed from wishlist.')
    return redirect('product_detail', product_slug=item_slug)



@login_required
def add_review(request, product_slug):
    if request.user.is_superuser:
        return HttpResponseForbidden('SuperUsers are not allowed to add reviews')
    
    product = get_object_or_404(Product, slug=product_slug)
    existing_review = Review.objects.filter(user=request.user, product=product).first()

    if existing_review:
        messages.warning(request, 'Review already has been added.')
        return redirect('product_detail', product_slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Review added.')
            return redirect('product_detail', product_slug=product.slug)
    else:
        form = ReviewForm()

    return render(request, 'product/add_review.html', {'form':form, 'product':product})




@login_required
def delete_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    reviews = Review.objects.filter(product=product, user=request.user).first()
    reviews.delete()
    messages.error(request, "Review deleted.")
    return redirect('product_detail', product_slug=product.slug)




def update_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    review = get_object_or_404(Review, product=product, user=request.user)
    if request.method=='POST':
        form = UpdateReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated.')
            return redirect('product_detail', product_slug=product.slug)
    else:
        form = UpdateReviewForm(instance=review)
    return render(request, 'product/update_review.html', {'form':form, 'product':product})




@user_passes_test(lambda u: u.is_superuser)
def users_listing(request):
    users = User.objects.all()
    users_details = []
    
    for user in users:
       if not user.is_superuser:
            users_details.append({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
            })
    context = {
        'users_details': users_details,
    }
    # for fields in User._meta.get_fields():
    #     print(fields)
    return render(request, 'product/users_details_listing.html', context)




@login_required
def add_to_cart(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    # product = get_object_or_404(Product,slug=product_slug) #same

    if product.stock == 0:
        messages.error(request, 'Product is out of stock')
        return redirect('product_detail', product_slug=product.slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    messages.success(request, 'Product added in cart.')

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, 'Product added in cart.')
    return redirect('product_detail', product_slug=product.slug)




@login_required
def update_cart(request, item_slug):
    cart_item = get_object_or_404(CartItem, slug=item_slug, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
        else:
            messages.error(request, "Quantity must be greater than 0 & less then available stock.")
    return redirect('cart_view')




@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    # Calculate discounted price and total price for each cart item
    for item in cart_items:
        item.discounted_price = round(item.product.price * (1 - item.product.discount / 100), 2)
        item.total_price = round(item.discounted_price * item.quantity, 2)

    total_cart_price = sum(item.total_price for item in cart_items)
    return render(request, 'product/cart.html', {'cart': cart, 'cart_items': cart_items, 'total_cart_price': total_cart_price})




@login_required
def remove_from_cart(request, item_slug):
    cart_item = get_object_or_404(CartItem, slug=item_slug, cart__user=request.user)
    cart_item.delete()
    messages.warning(request, 'Item removed from cart')
    return redirect('cart_view')



@login_required
def remove_cart_item(request, item_slug):
    cart_item = get_object_or_404(CartItem, slug=item_slug, cart__user=request.user)
    cart_item.delete()
    messages.warning(request, 'Item removed from cart')
    return redirect('product_detail', product_slug=item_slug)



def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            if address.is_default:
                address.set_default()
            return redirect('addresses')
    else:
        form = AddressForm(user=request.user)
    return render(request, 'product/add_address.html', {'form':form})


def manage_address(request):
    addresses = Address.objects.filter(user=request.user)
    signer = Signer()
    signed_addresses = []
    for address in addresses:
        encrypted_address = signer.sign(address.id)
        signed_addresses.append({
            'address':address,
            'encrypted_address': encrypted_address,
        })
    return render(request, 'product/manage_addresses.html', {'addresses': signed_addresses})


def set_default_address(request, encrypted_address):
    signer = Signer()
    try:
        address_id = signer.unsign(encrypted_address)
    except:
        return HttpResponse('Wrong address id getting')
    
    address = Address.objects.get(id=address_id, user=request.user)
    address.set_default()
    return redirect('addresses')


def delete_address(request, encrypted_address):
    signer = Signer()
    try:
        address_id = signer.unsign(encrypted_address)
    except:
        return HttpResponse('Wrong encrypted id')
    address = Address.objects.get(id=address_id, user=request.user)
    address.delete()
    return redirect('addresses')



def edit_address(request, encrypted_address):
    signer = Signer()
    try:
        address_id = signer.unsign(encrypted_address)
    except:
        return HttpResponse('Wrong address id getting')
    
    address = Address.objects.get(id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        address = form.save(commit=False)
        address.user = request.user
        address.save()

        if address.is_default:
            address.set_default()
        return redirect('addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'product/add_address.html', {'form':form})

    

def reviews_list(request):
    reviews = Review.objects.filter(user=request.user)
    
    return render(request, 'product/reviews_listing.html', {'reviews':reviews})

def account(request):
    return render(request, 'product/account.html')



class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'product/password_change.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)

        send_mail(
            'Your Password Has Been Changed',
            'Hello {}, \n\n Your password has been successfully chaged.\n\nIf you did not intiate this change, Please contact support immediately'.format(self.request.user.username),
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
            fail_silently=False,
        )
        return response





