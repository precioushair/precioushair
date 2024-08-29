from django.contrib.sitemaps import Sitemap
from django.db.models.base import Model
from django.urls import reverse
from core.models import Category, Product

class StaticSitemap(Sitemap):
    def items(self):
        return ['core:home','core:about','core:contact','core:faq','core:categories','core:products', 'userauths:sign-up-page']
    def location(self, item):
        return reverse(item)
    
class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all().order_by('-date')  
    
class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.all().order_by('-date')