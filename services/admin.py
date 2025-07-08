from django.contrib import admin
from .models import Service

# Register your models here.

@admin.register(Service)
class TotalStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'weight', 'bag_type', 'quantity', 'request_date', 'oic', 'is_billed', 'billed_date', 'email', 'notes')
    search_fields = ('company__name', 'bag_type__name', 'weight__name', 'oic', 'email', 'notes')
    list_filter = ('company', 'bag_type', 'weight', 'is_billed', 'request_date')
    list_per_page = 10