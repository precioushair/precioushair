from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact", views.contact, name="contact"),
    path("about", views.about, name="about"),
    path("faq", views.faq, name="faq"),

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
    
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),


    path('search_query/', views.search_queries, name='search_query'),
    path('search/', views.search, name='search'),
]

