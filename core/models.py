from django.db import models
from userauths.models import User
from django.utils.html import mark_safe
from django.conf import settings
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
          
cloudinary.config( 
  cloud_name = getattr(settings, 'CLOUD_NAME_SECRET', None), 
  api_key = getattr(settings, 'API_KEY', None), 
  api_secret = getattr(settings, 'API_SECRET', None)
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
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = CloudinaryField(folder="products")
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
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
            base_sku = slugify(self.name)[:10]  # Limiting to 10 characters for brevity
            unique_sku = f"{base_sku}-{uuid.uuid4().hex[:8]}"  # Adding 8 characters from a UUID
            self.sku = unique_sku
            # Update the image field with the resized image
            self.image = InMemoryUploadedFile(output, 'ImageField', 
                                              f"{self.image.public_id}.webp", 
                                              'image/webp', 
                                              output.getbuffer().nbytes, 
                                              None)

        # Call the original save method to save the model instance
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
    
class ProductImages(models.Model):
    images = CloudinaryField(folder="products")
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            # Download the image from Cloudinary
            response = requests.get(self.image.url)
            img = Image.open(BytesIO(response.content))

            # Resize the image to the desired dimensions (280x320)
            img = img.resize((280, 320), Image.ANTIALIAS)

            # Save the resized image to a BytesIO object
            output = BytesIO()
            img.save(output, format='WEBP', quality=98)
            output.seek(0)

            # Update the image field with the resized image
            self.image = InMemoryUploadedFile(output, 'ImageField', 
                                              f"{self.image.public_id}.webp", 
                                              'image/webp', 
                                              output.getbuffer().nbytes, 
                                              None)

        # Call the original save method to save the model instance
        super(ProductImages, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary before deleting the Blog object
        if self.images:
            # Get the public ID of the image from Cloudinary
            public_id = self.images.public_id
            # Delete the image from Cloudinary
            cloudinary.uploader.destroy(public_id)
        # Call the parent class delete method to delete the Blog object
        super().delete(*args, **kwargs)
    class Meta:
        verbose_name_plural = "Product images"
        
        


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
        return f'Order {self.id} by {self.customer.username}'
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


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage or fixed amount
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
