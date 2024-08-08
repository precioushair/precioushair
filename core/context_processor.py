from core.models import Category, Wishlist, Cart

def default(request):
    categories = Category.objects.all()
    user = request.user

    return {
        "categories": categories,
        "user": user,
    }

def wishlist_processor(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items = []
    return {'wishlist_items': wishlist_items}

def cart_context(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    cart_total = cart.get_total() if cart else 0

    return {
        'cart': cart,
        'cart_total': cart_total,
    }