from .models import Cart, Wishlist, Review

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            return {'cart_count': cart.items.count()}
        return {'cart_count': 0}
    return {'cart_count': 0}

    
        
    
def wishlist_count(request):
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            return {'wishlist_count': wishlist.items.count()}
        return {'wishlist_count': 0}
    return {'wishlist_count': 0}



def review_count(request):
    if request.user.is_authenticated:
        reviews = Review.objects.filter(user=request.user)
        return {'review_count': reviews.count()}  # Return count directly
    return {'review_count': 0}  # Return 0 if the user is not authenticated
