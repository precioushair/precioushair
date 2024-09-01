from django.contrib import admin
from core.models import Order, Product
from django.core.paginator import Paginator


class MyAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        total_orders = Order.objects.count()
        completed_orders = Order.objects.filter(complete=True).count()
        pending_orders = Order.objects.filter(complete=False).count()
        
        custom_context = {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
        }
        
        if extra_context is None:
            extra_context = {}
        extra_context.update(custom_context)
        
        return super().index(request, extra_context=extra_context) 


    

    
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

admin_site = MyAdminSite(name='myadmin')
admin_site.register(Order)
