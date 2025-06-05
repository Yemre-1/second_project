from django.contrib import admin
from .models import Product
from .models import Order, OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    list_editable = ('status',)  # Bu sayede liste üzerinden durum değiştirilebilir

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Product)