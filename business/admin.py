from django.contrib import admin
from core.models import Order, Product, Review, Coupon
from django.core.paginator import Paginator



    

    
class ProductAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Use the admin's default queryset
        queryset = self.get_queryset(request)
        
        # Order the queryset (you can use any field you prefer)
        queryset = queryset.order_by('name')
        
        # Pagination logic, just like in the example you provided
        paginator = Paginator(queryset, 12)  # Show 12 products per page
        page_number = request.GET.get('e')
        page_obj = paginator.get_page(page_number)

        # Update the context with paginated queryset
        extra_context = extra_context or {}
        extra_context['products'] = page_obj
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Product, ProductAdmin)


admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Coupon)