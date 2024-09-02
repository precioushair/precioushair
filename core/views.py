from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Wishlist,Cart, CartItem
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# Create your views here.





def home(request):
    products = Product.objects.all().order_by('-id')[:4]
    new_products = Product.objects.all().order_by('-id')[:5]

    context = {
        "products": products,
        "new_products": new_products,
    }
    return render(request, "core/index.html", context)


def about(request):
    return render(request, "core/about-us.html")


def contact(request):
    return render(request, "core/contact-us.html")

def faq(request):
    return render(request, "core/faq.html")

def all_products(request):
    products = Product.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,  # Pass the paginated products
    }
    return render(request, "product/all-products.html", context)

def category_list(request):
    return render(request, 'category/category-list.html')


def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category)
    list_mode = request.GET.get('list', 'false') == 'true'
    context = {
        'category': category,
        'products': products,
        'list_mode': list_mode,
    }


    if list_mode:
        template = 'category/category-detail-list.html'
    else:
        template = 'category/category-detail.html'
    return render(request, template, context)


def category_detail_list_mode(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter( category=category)
    context = {
        'category': category,
        'products': products,

    }
    return render(request, "htmx/category-detail-list.html", context)

def category_detail_grid_mode(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter( category=category)
    context = {
        'category': category,
        'products': products,

    }
    return render(request, "htmx/category-detail-grid.html", context)


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)

    context = {
        'product': product,
        'r_products': related_products
    }
    return render(request, "product/product-360-degree.html", context)



def product_preview(request, slug):
    product = Product.objects.get(slug=slug)
    p_image = product.p_images.all()
    context = {
        'product': product,
        'p_image': p_image,
    }
    return render(request, "htmx/product_details.html", context)



def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        
        wishlist_items = Wishlist.objects.filter(user=request.user)
        
        if created:
            # The product was added to the wishlist
            if 'HX-Request' in request.headers:
                return render(request, 'htmx/wishlist_items.html', {'wishlist_items': wishlist_items})
            return render(request, 'htmx/wishlist.html', {'wishlist_items': wishlist_items})
        else:
            # The product is already in the wishlist
            if 'HX-Request' in request.headers:
                return JsonResponse({'error': 'Product is already in your wishlist'}, status=200)
            return render(request, 'htmx/wishlist.html', {'wishlist_items': wishlist_items, 'message': 'Product is already in your wishlist'})

    return HttpResponse(status=403)

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        wishlist_items = Wishlist.objects.filter(user=request.user)
        if 'HX-Request' in request.headers:
            return render(request, 'htmx/wishlist_items.html', {'wishlist_items': wishlist_items})
        return HttpResponse(status=200)

    return HttpResponse(status=403)



@login_required
def view_wishlist(request):
    
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items = None

    return render(request, 'user/wishlist.html', {'wishlist_items': wishlist_items})


def view_cart(request):
    return render(request, "user/cart.html")

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return render(request, 'htmx/cart_items.html', {'cart_item': cart_item})

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()

    cart = get_cart(request)
    
    return render(request, 'htmx/cart_items.html', {'cart_item': cart_item, 'removed': True})

def search(request):
    return render(request, "core/search.html")


def search_queries(request):
    query = request.GET.get('query', '')
    
    # Return empty results if query is too short
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    # Perform a case-insensitive search using icontains
    top_products = Product.objects.filter(name__icontains=query).values('id', 'name', 'slug')[:10]

    return JsonResponse({'results': list(top_products)})
