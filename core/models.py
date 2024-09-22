from django.db import models
from userauths.models import User
from django.utils.html import mark_safe
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import cloudinary
from cloudinary.models import CloudinaryField
import uuid
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import requests
from decouple import config


cloudinary.config( 
  cloud_name = config('CLOUD_NAME_SECRET'), 
  api_key = config('CLOUDINARY_API_KEY'), 
  api_secret = config('CLOUDINARY_API_SECRET')
)
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = CloudinaryField(folder="category-images")
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def product_count(self):
        return self.products.count()

    def get_absolute_url(self):
        return f'/categories/{self.slug}/'
    def save(self, *args, **kwargs):
        if self.image:
            # Download the image from Cloudinary
            response = requests.get(self.image.url)
            img = Image.open(BytesIO(response.content))

            # Resize the image to the desired dimensions (280x320)
            img = img.resize((280, 320), Image.ANTIALIAS)

            # Save the resized image to a BytesIO object
            output = BytesIO()
            img.save(output, format='WEBP', quality=100)
            output.seek(0)

            # Update the image field with the resized image
            self.image = InMemoryUploadedFile(output, 'ImageField', 
                                              f"{self.image.public_id}.webp", 
                                              'image/webp', 
                                              output.getbuffer().nbytes, 
                                              None)

        # Call the original save method to save the model instance
        super(Category, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary before deleting the Blog object
        if self.image:
            # Get the public ID of the image from Cloudinary
            public_id = self.image.public_id
            # Delete the image from Cloudinary
            cloudinary.uploader.destroy(public_id)
        # Call the parent class delete method to delete the Blog object
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = CloudinaryField(folder="products")
    image1 = CloudinaryField(folder="products", default="product.webp", blank=True)
    image2 = CloudinaryField(folder="products", default="product.webp", blank=True)
    image3 = CloudinaryField(folder="products", default="product.webp", blank=True)
    COLOR_CHOICES = [
        ('black', 'Black'),
        ('brown', 'Brown'),
        ('blonde', 'Blonde'),
        ('ombre', 'Ombré'),
        ('highlighted', 'Highlighted'),
        ('red', 'Red'),
        ('custom', 'Custom'),
    ]
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, null=True)
    
    # Size options for hair lengths
    SIZE_CHOICES = [
        ('12', '12 Inches'),
        ('14', '14 Inches'),
        ('16', '16 Inches'),
        ('18', '18 Inches'),
        ('20', '20 Inches'),
        ('22', '22 Inches'),
        ('24', '24 Inches'),
        ('26', '26 Inches'),
    ]
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_best_seller = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    def blog_image(self):
        return mark_safe('<img src="%s" width="50" height="50" style="border-radius: 5px;" />' % (self.image.url))
    def __str__(self):
        return self.name
    def is_recent(self):
        return self.date >= timezone.now() - timedelta(days=2)
    def finished(self):
        return self.stock <= 0
    def get_absolute_url(self):
        return f'/products/{self.slug}/'
    def save(self, *args, **kwargs):
        
        if self.image and not self.sku:
            # Generate a unique SKU only if it doesn't already exist
            unique_sku = f"{uuid.uuid4().hex[:8]}"  # Adding 8 characters from a UUID
            self.sku = unique_sku
        if not self.slug:
            self.slug = slugify(self.name)

        # Save the instance first to ensure the image is uploaded to Cloudinary
        super(Product, self).save(*args, **kwargs)

        
    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary before deleting the Blog object
        if self.image:
            # Get the public ID of the image from Cloudinary
            public_id = self.image.public_id
            # Delete the image from Cloudinary
            cloudinary.uploader.destroy(public_id)
        # Call the parent class delete method to delete the Blog object
        super().delete(*args, **kwargs)
    
        

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        return self.product.name
    @classmethod
    def clear_wishlist(cls, user):
        """Clears all wishlist items for the specified user."""
        cls.objects.filter(user=user).delete()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user or 'Anonymous'}"
    
    def get_total(self):
        total = sum(item.product.price * item.quantity for item in self.items.all())
        return total
    def get_quantity_of_product(self, product):
        try:
            cart_item = self.items.get(product=product)
            return cart_item.quantity
        except CartItem.DoesNotExist:
            return 0  # Return 0 if the product is not in the cart

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    



class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)  
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    
    def __str__(self):
        return f'Order {self.id} by {self.customer.full_name}'
    def calculate_total(self):
        total = sum(item.product.price * item.quantity for item in self.items.all())
        if self.coupon:
            discount = (self.coupon.discount / 100) * total  # Assuming the discount is a percentage
            total -= discount
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
  
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipping_addresses")
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Shipping Address for {self.user.full_name} - {self.address_line_1}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'Review by {self.user.full_name} for {self.product.name}'


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage or fixed amount
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Admin receiving the notification
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} - {self.message[:20]}'