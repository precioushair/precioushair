from django.shortcuts import render, redirect
from django.conf import settings
from core.models import Cart, Order, OrderItem, Product, Notification
from django.shortcuts import get_object_or_404
from .forms import PaymentForm
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse



def initiate_payment(request):
    cart = Cart.objects.get(user=request.user)
    total = cart.get_total() * 100  # Convert to kobo

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json',
            }
            data = {
                "email": form.cleaned_data['email'],
                "amount": total,
            }
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=data)
            res_data = response.json()
            if res_data['status']:
                return redirect(res_data['data']['authorization_url'])
            else:
                # Handle error
                return render(request, 'payment/error.html', {'message': res_data['message']})
    else:
        form = PaymentForm(initial={'amount': total})

    return render(request, 'payment/initiate_payment.html', {'form': form, 'cart': cart})


def verify_payment(request):
    reference = request.GET.get('reference')
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
    res_data = response.json()

    if res_data['status'] and res_data['data']['status'] == 'success':
        # Payment was successful
        # Create the Order and OrderItems from the Cart
        cart = Cart.objects.get(user=request.user)
        order = Order.objects.create(customer=request.user, complete=True)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        
        # Clear the cart
        cart.items.all().delete()

        return HttpResponse("Payment Successful")
    else:
        # Handle payment failure
        return HttpResponse("Payment Failed")



def mail_view(request):
    return render(request, "admin/mail.html")


def is_admin_user(user):
    return user.is_staff  # Only allow staff (admin) users


@user_passes_test(is_admin_user)
def recent_orders(request):
    # Fetch recent orders for the logged-in admin user
    recent_orders = Order.objects.order_by('-created_at')[:5]  # Limit to 5 recent orders

    # Prepare data to return as JSON
    orders_data = []
    for order in recent_orders:
        orders_data.append({
            'order_id': order.id,
            'customer_email': order.customer.email,
            'customer_name': order.customer.full_name,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': 'Completed' if order.complete else 'Pending',
            'total': order.calculate_total(),  # Assuming you have a total calculation method
        })

    return JsonResponse({'orders': orders_data})

@user_passes_test(is_admin_user)  # Ensure only admins can access this
def orders_summary(request):
    # Calculate total orders
    total_orders = Order.objects.count()

    # Calculate total earnings by summing the total from each order
    orders = Order.objects.filter(complete=True)
    total_earnings = sum(order.calculate_total() for order in orders)

    # Return the data as JSON
    data = {
        'total_orders': total_orders,
        'total_earnings': total_earnings,
    }
    return JsonResponse(data)


@user_passes_test(is_admin_user)  # Ensure only admins can access this
def admin_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    unread_count = notifications.filter(is_read=False).count()

    notification_list = [
        {
            'message': notification.message,
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': notification.is_read
        }
        for notification in notifications
    ]

    return JsonResponse({
        'notifications': notification_list,
        'unread_count': unread_count,
    })