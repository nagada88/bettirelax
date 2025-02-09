from django.db import models
from app_bettirelax.models import Service, ServicePrice
from django.contrib.auth.models import User

# Create your models here.
class OpeningHours(models.Model):
    DAY_CHOICES = [
        (0, 'Hétfő'),
        (1, 'Kedd'),
        (2, 'Szerda'),
        (3, 'Csütörtök'),
        (4, 'Péntek'),
        (5, 'Szombat'),
        (6, 'Vasárnap'),
    ]

    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="Nap")
    is_even_week = models.BooleanField(default=True, verbose_name="Páros hét?")  
    start_time = models.TimeField(verbose_name="Nyitás")
    end_time = models.TimeField(verbose_name="Zárás")

    def __str__(self):
        week_type = "Páros hét" if self.is_even_week else "Páratlan hét"
        return f"{self.get_day_of_week_display()} ({week_type}): {self.start_time} - {self.end_time}"

    class Meta:
        verbose_name = "Nyitvatartás"
        verbose_name_plural = "Nyitvatartások"
        unique_together = ('day_of_week', 'is_even_week', 'start_time', 'end_time')

class BookingSettings(models.Model):
    is_booking_enabled = models.BooleanField(default=True, verbose_name="Foglalási rendszer bekapcsolva?")
    max_weeks_in_advance = models.PositiveIntegerField(default=4, verbose_name="Hány hétre előre lehet foglalni? (1-12)", choices=[(i, f"{i} hét") for i in range(1, 13)])
    min_hours_before_booking = models.PositiveIntegerField(default=24, verbose_name="Legkésőbb mennyivel előre lehet foglalni? (órákban)")
    auto_reject_time = models.PositiveIntegerField(default=12, verbose_name="Mennyi idő után utasítsuk el automatikusan? (órákban)")

    def __str__(self):
        return "Foglalási rendszer beállításai"

    class Meta:
        verbose_name = "Foglalási beállítások"
        verbose_name_plural = "Foglalási beállítások"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Függőben'),
        ('accepted', 'Elfogadva'),
        ('cancelled', 'Lemondva'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Foglaló")
    date = models.DateField(verbose_name="Dátum", null=True) 
    start_time = models.TimeField(verbose_name="Kezdés")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    customer_name = models.CharField(max_length=255, default='', verbose_name="Foglaló neve",)
    customer_email = models.EmailField(default='', verbose_name="Foglaló email címe")
    booked_service_type = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, verbose_name="Foglalt szolgáltatás")
    booked_service_length = models.PositiveIntegerField(default=30, verbose_name="Szolgáltatás időtartama (perc)")
    booked_service_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Szolgáltatás ára (Ft)")
    billing_address = models.TextField(default='', verbose_name="Számlázási cím")
    billing_name = models.CharField(max_length=255, default='', verbose_name="Számlázási név")
    billing_email = models.EmailField(default='', verbose_name="Számlázási email")

    def __str__(self):
        return f"{self.customer_name} - {self.booked_service_type.service_name} ({self.date} {self.start_time})"

