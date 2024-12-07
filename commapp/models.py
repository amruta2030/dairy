
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

STATE_CHOICES = (
    ('Andaman & Nicobar Island','Andaman & Nicobar Island'),
    ('Andhra Pradesh','Andhra Pradesh'),
    ('ArunachalPradesh','ArunachalPradesh'),
    ('Assam','Assam'),
    ('Bihar','Bihar'),
    ('Chandigarh','Chandigarh'),
    ('Chatisgarh','Chatisgarh'),
    ('Dadra & Nagar Haveli','Dadra & Nagar Haveli'),
    ('Daman & Diu','Daman & Diu'),
    ('Delhi','Delhi'),
    ('Goa','Goa'),
    ('Gurat','Gurat'),
    ('Haryana','Haryana'),
    ('Himachal Pradesh','Himachal Pradesh'),
    ('Jammu & Kashmir','Jammu & Kashmir'),
    ('Jharkhand','Jharkhand'),
    ('Karnataka','Karnataka'),
    ('Kerla','Kerla'),
    ('Lakshawdweep','Lakshawdweep'),
    ('Madhya Pradesh','Madhya Pradesh'),
    ('Maharashtra','Maharastra'),
    ('Manipur','Manipur'),
    ('Meghalaya','Meghalaya'),
    ('Mizoram','Mizoram'),
    ('Odisha','Odisha'),
    ('Puduchery','Puduchery'),
    ('Punjab','Punjab'),
    ('Rajasthan','Rajasthan'),
    ('Sikkim','Sikki'),
    ('Tamilnadu','Tamilnadu'),
    ('Telengana','Telengana'),
    ('Tripura','Tripura'),
    ('Utter Pradesh','Utter Pradesh'),
    ('Uttrakhand','Uttrakhand'),
    ('West Bengal','West Bengal'),
)

CATEGORY_CHOICE=(
    ('CR','Curd'),
    ('ML','Milk'),
    ('LS','Lassi'),
    ('MS','MilkShake'),
    ('PN','Paneer'),
    ('GH','Ghee'),
    ('CZ','Cheese'),
    ('IC','ice-Cream'),
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICE, max_length=2)  # Correct field type
    product_image = models.ImageField(upload_to='product')

    def __str__(self):
        return self.title

    
    
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=100)
    def __str__(self):
        return self.name
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Lowercase field name
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
 
 
STATUS_CHOICES = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('on the way','on the way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Pending','Pending'),
) 
 
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)
    
    def get_payment_id(self):
        """Return Razorpay payment ID or a default value."""
        return self.razorpay_payment_id or "N/A"
    
    def __str__(self):
        return f"Payment {self.id} by {self.user}"
    
    
# class OrderPlaced(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
#     product = models.ForeignKey(Product,on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     ordered_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='Pending')
#     payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")  
#     # @property
#     # def total_cost(self):
#     #     return self.quantity * self.product.discounted_price
    
#     def __str__(self):
#         return f"Order {self.id} by {self.user.username}"

from django.db import models
from django.contrib.auth.models import User
from .models import Customer, Product, Payment

class OrderPlaced(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
