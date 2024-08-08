from django.contrib import admin
from .models import User, Contact
from django.contrib.auth.models import Group

admin.site.unregister(Group)

class UserAdmin(admin.ModelAdmin):
    list_display = ['full_name','email',"phone_number"]
class ContactAdmin(admin.ModelAdmin):
    list_display = ['first_name','email',"contact", "message"]



admin.site.register(User, UserAdmin)
admin.site.register(Contact, ContactAdmin)
