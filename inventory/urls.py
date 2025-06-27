from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path("stock/", views.total_stock_list, name="total_stock_list"),

    path("flow/", views.inventory_flow, name="inventory_flow"),
    path("add-stock/", views.add_stock_view, name='add_stock'),
    path("flow/delete/<int:pk>/", views.delete_flow_view, name='delete_flow'),
]
