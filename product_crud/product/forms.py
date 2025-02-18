from django import forms
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from .models import UserProfile, Product, Review, Address
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class CustomResetPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"})
    )



class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password", 
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new password"})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password", 
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"})
    )



class UserSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Create a username'})
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    password1 = forms.CharField(
        required=True,
        label='Password',  
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password'})
    )
    password2 = forms.CharField(
        required=True,
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )
     # OTPForm field
    otp = forms.CharField(
        max_length=6, 
        required=True,
        label='OTP',  
        widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','email', 'password1', 'password2', 'otp']

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        # Customizing form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  
    
    def clean_emai(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email


            
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mobile_no', 'address', 'profile_pic']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'stock', 'image']
    
    def save(self, commit=True):
        product = super().save(commit=False)
        if not product.slug:  
            product.slug = slugify(product.name)
        if commit:
            product.save()
        return product 

        

class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'stock', 'image']



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }



class UpdateReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']



class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name', 'phone_number', 'alt_phone_number', 
            'pincode', 'state', 'city', 'house_no_or_building_name',
            'area_or_colony', 'nearby_landmark', 'address_type', 'is_default'
        ]
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['address_type'].queryset = Address.objects.filter(user=user)



class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

