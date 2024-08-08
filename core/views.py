from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Wishlist,Cart, CartItem
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
# Create your views here.


# Initialize the vectorizer and TF-IDF matrix globally to avoid recomputation
products = Product.objects.all().values_list('id', 'name', 'slug')
products_df = pd.DataFrame(list(products), columns=['id', 'name', 'slug'])
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 4))
tfidf_matrix = vectorizer.fit_transform(products_df['name'])



def home(request):
    products = Product.objects.all()

    context = {
        "products": products,
    }
    return render(request, "core/index.html", context)


def about(request):
    return render(request, "core/about-us.html")


def contact(request):
    return render(request, "core/contact-us.html")

def faq(request):
    return render(request, "core/faq.html")



def category_list(request):
    return render(request, 'category/category-list.html')


def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter( category=category)
    context = {
        'category': category,
        'products': products
    }
    return render(request, "category/category-detail.html", context)


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)

    context = {
        'product': product
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


def search_queries(request):
    query = request.GET.get('query', '')
    if len(query) < 3:
        return JsonResponse({'results': []})

    # Transform the query
    query_vec = vectorizer.transform([query])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Set a similarity threshold
    similarity_threshold = 0.05

    # Get indices of products that meet the similarity threshold
    filtered_indices = [i for i, score in enumerate(similarity) if score >= similarity_threshold]

    # Sort filtered indices by similarity score in descending order
    sorted_indices = sorted(filtered_indices, key=lambda i: similarity[i], reverse=True)

    # Limit the number of results to return
    top_n = 10
    sorted_indices = sorted_indices[:top_n]

    # Retrieve the top products
    product_ids = [products_df.iloc[i]['id'] for i in sorted_indices]
    top_products = Product.objects.filter(id__in=product_ids).in_bulk(product_ids)

    # Prepare the results
    results = []
    for i in sorted_indices:
        product = top_products[products_df.iloc[i]['id']]
        results.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
        })

    return JsonResponse({'results': results})

def search(request):
    return render(request, "core/search.html")