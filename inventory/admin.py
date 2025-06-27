from django.contrib import admin
from .models import Company, Weight, BagType, InventoryFlow, TotalStock


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(BagType)
class BagTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(InventoryFlow)
class InventoryFlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'weight', 'bag_type', 'quantity', 'movement_date')
    search_fields = ('company__name', 'bag_type__name', 'weight__name')
    list_filter = ('company', 'bag_type', 'weight', 'movement_date')


@admin.register(TotalStock)
class TotalStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'weight', 'bag_type', 'quantity')
    search_fields = ('company__name', 'bag_type__name', 'weight__name')
    list_filter = ('company', 'bag_type', 'weight')
