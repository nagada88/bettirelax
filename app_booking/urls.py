from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
        path("admin/foglalas-letrehozasa/", views.admin_create_booking, name="admin_create_booking"), 
        path("booking/", views.booking_view, name="booking_view"),
        path("api/available_slots/", views.get_available_slots, name="get_available_slots"),   
    ]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)