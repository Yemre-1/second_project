from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings
from django.utils import timezone

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    new_email= models.EmailField()
    token= models.UUIDField(default=uuid.uuid4, unique=True)
    created_at= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}-{self.new_email}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/' , default='avatars/default.png' ,null=True, blank=True)
    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name    
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description= models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock= models.PositiveIntegerField(default=0)
    category= models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user} s cart"
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity= models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"  
    def get_total_price(self):
        return self.product.price * self.quantity
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('shipped', 'Kargolandı'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    # diğer alanlar

    def __str__(self):
        return f"Sipariş #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order= models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity= models.PositiveIntegerField()  
class Comment(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content= models.TextField('Yorum')
    created_at= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
