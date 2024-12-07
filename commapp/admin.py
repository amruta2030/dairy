from django.contrib import admin
from .models import OrderPlaced, Payment, Product, Customer, Cart  # Import models from the same app

# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','discounted_price','category','product_image']
    
 

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','locality','city','state','zipcode']   


@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']


@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'amount',
        'razorpay_order_id',
        'razorpay_payment_status',
        'get_payment_id',  # Call the method instead of accessing the field directly
        'paid'
    ]
    list_display_links = ['id', 'user']  # Optional: make fields clickable
    
    def get_payment_id(self):
        return self.razorpay_payment_id or "N/A"
    
@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer','product','quantity','ordered_date','status','payment']
    list_filter = ['status', 'ordered_date']
    search_fields = ['user__username', 'customer__locality', 'product__title']
