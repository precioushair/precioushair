from django.db import models
from userauths.models import User
# Create your models here.
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', default="category.webp")
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        if self.image:
            # Open the uploaded image
            img = Image.open(self.image)

            # Resize the image to the desired dimensions (280x280)
            img = img.resize((612, 406), Image.ANTIALIAS)

            # Save the resized image to a BytesIO object
            output = BytesIO()
            img.save(output, format='WEBP', quality=98)
            output.seek(0)

            # Update the image field with the resized image
            self.image = InMemoryUploadedFile(output, 'ImageField', 
                                             f"{self.image.name.split('.')[0]}.webp", 
                                             'image/webp', 
                                             output.getbuffer().nbytes, 
                                             None)

        # Call the original save method to save the model instance
        super(Category, self).save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            # Open the uploaded image
            img = Image.open(self.image)

            # Resize the image to the desired dimensions (280x280)
            img = img.resize((280, 320), Image.ANTIALIAS)

            # Save the resized image to a BytesIO object
            output = BytesIO()
            img.save(output, format='WEBP', quality=98)
            output.seek(0)

            # Update the image field with the resized image
            self.image = InMemoryUploadedFile(output, 'ImageField', 
                                             f"{self.image.name.split('.')[0]}.webp", 
                                             'image/webp', 
                                             output.getbuffer().nbytes, 
                                             None)

        # Call the original save method to save the model instance
        super(Product, self).save(*args, **kwargs)
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to='products/')
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            # Open the uploaded image
            img = Image.open(self.image)

            # Resize the image to the desired dimensions (280x280)
            img = img.resize((280, 320), Image.ANTIALIAS)

            # Save the resized image to a BytesIO object
            output = BytesIO()
            img.save(output, format='WEBP', quality=98)
            output.seek(0)

            # Update the image field with the resized image
            self.images = InMemoryUploadedFile(output, 'ImageField', 
                                             f"{self.images.name.split('.')[0]}.webp", 
                                             'image/webp', 
                                             output.getbuffer().nbytes, 
                                             None)

        # Call the original save method to save the model instance
        super(ProductImages, self).save(*args, **kwargs)
    
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

    def __str__(self):
        return f'Order {self.id} by {self.customer.username}'

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

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'