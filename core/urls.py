from django.urls import path
from . import views
from .utils import get_cities
app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact", views.contact, name="contact"),
    path("about", views.about, name="about"),
    path("faq", views.faq, name="faq"),

    path("trending", views.trending, name="trending"),
    path("best-sellers", views.best_sellers, name="best_sellers"),

    path("all-products", views.all_products, name="products"),
    path('products/<slug>', views.product_detail, name="product-detail" ),
    path('products/preview/<slug>', views.product_preview, name="product-preview" ),


    path('categories/', views.category_list, name="categories" ),
    path('categories/<slug>', views.category_detail, name="category-detail" ),
    path('categories_detail_list_mode/<slug>', views.category_detail_list_mode, name="category-detail-list-mode" ),
    path('categories_detail_grid_mode/<slug>', views.category_detail_grid_mode, name="category-detail-grid-mode" ),

    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<order_id>', views.order_view, name='order'),

    
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('api/cities/<str:state>/', get_cities, name='get_cities'),
    path('search_query/', views.search_queries, name='search_query'),
    path('search/', views.search_view, name='search'),
]

