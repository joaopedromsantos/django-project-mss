from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path("", views.total_services_list, name="services_list"),
    path("create/", views.create_service, name='create_service'),
    path("update/<int:pk>/", views.update_service, name='update_service'),
    path("delete/<int:pk>/", views.delete_service, name='delete_service'),
    path("details/<int:pk>/", views.get_service_details, name='get_service_details'),path("delete/<int:pk>/", views.delete_service, name='delete_service'),
]
