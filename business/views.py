from django.shortcuts import render, redirect
from django.conf import settings
from core.models import Cart, Order, OrderItem, Product
from django.shortcuts import get_object_or_404
from .forms import PaymentForm
import requests
from django.http import HttpResponse
from django.shortcuts import render

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


