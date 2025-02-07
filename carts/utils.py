from carts.models import Cart


def get_user_carts(request):
    if request.user.is_authenticated:
        # Return carts for authenticated users
        return Cart.objects.filter(user=request.user).select_related('product')
    
    # Ensure session is initialized for anonymous users
    if not request.session.session_key:
        request.session.create()
    
    # Return carts for anonymous users based on session key
    return Cart.objects.filter(session_key=request.session.session_key)