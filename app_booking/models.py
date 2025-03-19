from django.db import models
from app_bettirelax.models import Service, ServicePrice
from django.contrib.auth.models import User
from django_quill.fields import QuillField
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
import re

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
    is_reviews_enabled = models.BooleanField(default=True, verbose_name="Reviewk megjenítése?")
    max_weeks_in_advance = models.PositiveIntegerField(default=4, verbose_name="Hány hétre előre lehet foglalni? (1-12)", choices=[(i, f"{i} hét") for i in range(1, 13)])
    min_hours_before_booking = models.PositiveIntegerField(default=24, verbose_name="Legkésőbb mennyivel előre lehet foglalni? (órákban)")
    auto_reject_time = models.PositiveIntegerField(default=12, verbose_name="Mennyi idő után utasítsuk el automatikusan? (órákban)")
    booking_puffer =  models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name="puffer idő (percekben)")

    terms_conditions_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True, verbose_name="Felhasználási feltételek PDF")
    contraindications_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True, verbose_name="Ellenjavallatok PDF")
    privacy_policy_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True, verbose_name="Adatvédelmi irányelvek PDF")

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
        ('post_cancelled', 'Utólag Lemondva'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, editable=False,  verbose_name="Foglaló")
    date = models.DateField(verbose_name="Dátum", null=True) 
    start_time = models.TimeField(verbose_name="Kezdés")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Foglalás státusza')
    booked_service_type = models.CharField(max_length=30, default="", verbose_name='Masszázs fajtája')

    customer_name = models.CharField(max_length=255, default='', verbose_name="Foglaló neve",)
    customer_email = models.EmailField(default='', verbose_name="Foglaló email címe")
    customer_phone = models.CharField(max_length=20, default='', verbose_name="Vevő telefonszáma")

    booked_service_length = models.PositiveIntegerField(default=30, verbose_name="Szolgáltatás időtartama (perc)")
    booked_service_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Szolgáltatás ára (Ft)")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    admin_token = models.CharField(max_length=64, unique=True, blank=True, editable=False, null=True)  # 🔑 Új mező

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Ellenőrizzük, hogy új objektum-e

        if is_new:
            self.send_status_email() 

        elif not is_new:  # Csak meglévő objektum esetén ellenőrizzük a státuszt
            original = Booking.objects.get(pk=self.pk)
            if original.status != self.status:
                self.send_status_email()  # Automatikusan küldünk emailt a státusz változáskor

        super().save(*args, **kwargs)  # Mentjük az objektumot

    def send_status_email(self):
        """Email küldés a foglalás státuszának változása esetén."""
        subject = ""

        try:
            template = EmailTemplate.objects.get(type=self.status)  # A státusznak megfelelő sablon lekérése
            email_body = template.content.html  # HTML verzió
            
            # HTML tagek helyettesítése új sorokkal
            plain_body = re.sub(r'<br\s*/?>', '\n', email_body)  # <br> → új sor
            plain_body = re.sub(r'</p>', '\n', plain_body)  # </p> → új sor
            plain_body = strip_tags(plain_body).strip()  # Eltávolítjuk a maradék HTML-t
        except EmailTemplate.DoesNotExist:
            plain_body = "Tisztelt ügyfelünk,\n\nA foglalásával kapcsolatban változás történt."

        # Foglalás adatai blokk
        booking_details = (
            f"\n\nFoglalás adatai:\n"
            f"Időpont: {self.date} {self.start_time.strftime('%H:%M')}\n"
            f"Szolgáltatás: {self.booked_service_type}\n"
            f"Név: {self.customer_name}\n"
            f"Email: {self.customer_email}\n"
            f"Státusz: {self.get_status_display()}\n"
        )

        # Email teljes tartalmának összeállítása
        message = plain_body + booking_details

        # Email tárgy beállítása
        if self.status == "accepted":
            subject = "Foglalásod megerősítve - Betti Relax"
        elif self.status == "pending":
            subject = "Foglalásod fogadtuk - Betti Relax"
        elif self.status == "cancelled":
            subject = "Foglalásod törölve - Betti Relax"
        elif self.status == "post_cancelled":
            subject = "Fontos: foglalásod törlésre került - Betti Relax"

        if subject:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [self.customer_email],
                fail_silently=False,
            )

    def __str__(self):
        return f"{self.customer_name} - {self.booked_service_type} ({self.date} {self.start_time})"
    
class EmailTemplate(models.Model):
    TYPE_CHOICES = [ 
        ("pending", "Függőben lévő foglalás"),
        ("accepted", "Elfogadott foglalás"),
        ("cancelled", "Elutasított foglalás"),
        ("post_cancelled", "Utólag elutasított foglalás"),
        ("reminder", "Foglalási emlékeztető"),
    ]

    type = models.CharField(max_length=30, choices=TYPE_CHOICES, unique=True)
    content = QuillField()

    def __str__(self):
        return dict(self.TYPE_CHOICES).get(self.type, self.type)
    
    class Meta:
        verbose_name = "Email sablon"
        verbose_name_plural = "Email sablonok"