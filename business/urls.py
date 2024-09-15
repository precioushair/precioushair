from django.urls import path
from .views import initiate_payment, verify_payment, mail_view
from django.contrib import admin

app_name = "business"
urlpatterns = [
    path('pay/', initiate_payment, name='initiate_payment'),
    path('verify/', verify_payment, name='verify_payment'),
    path("admin-site/mail/", mail_view, name='mail_view'),

]
