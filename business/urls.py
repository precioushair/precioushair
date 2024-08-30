from django.urls import path
from .views import initiate_payment, verify_payment

urlpatterns = [
    path('pay/', initiate_payment, name='initiate_payment'),
    path('verify/', verify_payment, name='verify_payment'),
]
