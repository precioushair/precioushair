from django.urls import path
from .views import initiate_payment, verify_payment, mail_view, recent_orders, orders_summary, admin_notifications
from django.contrib import admin

app_name = "business"
urlpatterns = [
    path('pay/', initiate_payment, name='initiate_payment'),
    path('verify/', verify_payment, name='verify_payment'),
    path("admin-site/mail/", mail_view, name='mail_view'),
    path('api/recent-orders/', recent_orders, name='recent_orders'),
    path('api/orders-summary/', orders_summary, name='orders-summary'),
    path('api/notifications/', admin_notifications, name='admin_notifications'),

]
