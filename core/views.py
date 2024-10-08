from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Wishlist,Cart, CartItem, Coupon, Order, ShippingAddress, OrderItem
from .forms import ShippingAddressForm
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Q
from itertools import chain
# Create your views here.





def home(request):
    products = Product.objects.all().order_by('-id')[:4]
    new_products = Product.objects.all().order_by('-id')[:4]

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
    products = Product.objects.all().order_by('-id')
    
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
    products = Product.objects.filter(category=category).order_by('-id')
        # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    list_mode = request.GET.get('list', 'false') == 'true'
    context = {
        'category': category,
        'products': page_obj,
        'list_mode': list_mode,
    }


    if list_mode:
        template = 'category/category-detail-list.html'
    else:
        template = 'category/category-detail.html'
    return render(request, template, context)


def category_detail_list_mode(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter( category=category).order_by('-id')
        # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,

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
    context = {
        'product': product,
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



def search_queries(request):
    query = request.GET.get('query', '').strip()
    
    # Return empty results if query is too short
    if len(query) < 3:
        return JsonResponse({'results': [], 'message': ''})

    # Generate a cache key based on the query
    cache_key = f'search_results_{query}'
    cached_results = cache.get(cache_key)

    if cached_results is not None:
        return JsonResponse({'results': cached_results})

    try:
        # Fetch the products and only select the necessary fields
        top_products = Product.objects.filter(name__icontains=query).only('id', 'name', 'slug', 'image')[:10]

        if not top_products:
            return JsonResponse({'results': [], 'message': 'No results'})

        results = [{
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'image': product.image.url  # Extract the URL from the Cloudinary image field
        } for product in top_products]

        # Cache the results for 5 minutes
        cache.set(cache_key, results, 300)

        return JsonResponse({'results': results})

    except ObjectDoesNotExist:
        return JsonResponse({'results': [], 'message': 'No results'})
    except Exception as e:
        return JsonResponse({'results': [], 'message': str(e)})
    

def apply_coupon(request):
    coupon_code = request.POST.get('coupon_code', '').strip()
    
    # Check if the coupon code is provided
    if not coupon_code:
        return JsonResponse({'error': 'Please enter a coupon code.'}, status=400)
    
    try:
        # Get the coupon from the database
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)

        # Check if the coupon is still valid (within the valid_from and valid_until date range)
        if coupon.valid_from <= timezone.now() <= coupon.valid_until:
            # Coupon is valid, apply the discount
            # You can add logic to update the order total here
            return JsonResponse({'success': 'Coupon applied successfully!'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid or expired coupon code.'}, status=400)
    
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired coupon code.'}, status=400)
    

def update_cart(request):
    if request.method == "POST":
        cart = get_cart(request)
        items = request.POST.getlist('items[]')

        for item in items:
            try:
                product_id, quantity = item.split('|')
                product = get_object_or_404(Product, id=product_id)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                cart_item.quantity = int(quantity)
                cart_item.save()
            except ValueError:
                continue  # Skip malformed items
        
        context = {'cart': cart}
        html = render_to_string('htmx/cart_item_checkout.html', context, request=request)
        return HttpResponse(html)
    return HttpResponse(status=400)  # Return a bad request response if not POST

def view_cart(request):
    shipping_form = ShippingAddressForm()
    context ={'shipping_form': shipping_form}
    
    return render(request, "user/cart.html", context)


@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        # Create a new order instance
        order = Order.objects.create(customer=request.user, complete=False)
        shipping_option = request.POST.get('shipping_option')
        shipping_form = ShippingAddressForm(request.POST)

        if shipping_option == 'pickup':
            order.shipping_option = 'pickup'
            order.save()
            messages.success(request, 'Order created for pickup.')

            # Redirect to cart.html
            return redirect('core:order', order.id)  # Replace 'cart' with the actual name of the URL pattern for your cart page

        elif shipping_form.is_valid():
            shipping_address = shipping_form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.order = order
            shipping_address.save()

            # Create OrderItems from CartItems
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )

            # Clear cart items after creating order
            cart.items.all().delete()

            messages.success(request, 'Order created with shipping.')
            return redirect('core:order', order.id) 

        # Handle form validation error
        messages.error(request, 'Form validation failed.')
        return redirect('core:view_cart')  # Redirect back to cart.html

    # If the request method is not POST, render the cart page
    return render(request, 'user/cart.html', {'cart': cart})


def order_view(request, order_id):
    # Get the order by ID, ensuring it belongs to the logged-in user
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # Get the shipping address for the order
    shipping_address = order.shipping_addresses.first()

    # Get all items in the order
    order_items = order.items.all()

    # Pass the details to the template
    context = {
        'order': order,
        'shipping_address': shipping_address,
        'order_items': order_items,
        'total': order.calculate_total()  # Optional, if you want to show the total
    }

    return render(request, "product/order.html", context)

def best_sellers(request):
    products = Product.objects.filter(is_best_seller=True).order_by('-id')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,  # Pass the paginated products
    }
    return render(request, "product/all-products.html", context)

def trending(request):
    products = Product.objects.filter(is_trending=True).order_by('-id')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,  # Pass the paginated products
    }
    return render(request, "product/all-products.html", context)



def search_view(request):
    query = request.GET.get('search', '')  # Get the search term from the query string
    products = []

    if query:
        # Search through Category names and Product names
        products = Product.objects.filter(Q(name__icontains=query))


    context = {
        'query': query,
        'search_results': products,
        'count': products.count(),
    }

    return render(request, 'product/search.html', context)