from django.db import models
from PIL import Image
from io import BytesIO
import os
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.base import ContentFile
from sorl.thumbnail import get_thumbnail
from django.utils.html import format_html
from django.conf import settings
from django.conf.urls.static import static
from django_quill.fields import QuillField
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.utils.text import slugify
from PIL import Image, ExifTags
# Create your models here.


class ImageHandlerMixin:
    def save(self, *args, **kwargs):
        image_fields = getattr(self, 'IMAGE_FIELDS', [])
        print('idelegalabbbefutunk')
        # Mentsük először az eredeti képeket, hogy elérhetőek legyenek a thumbnail készítéshez
        super().save(*args, **kwargs)

        for field_name in image_fields:
            image_field = getattr(self, field_name, None)
            image_field.open()  # Nyisd meg a fájlt, ha zárt
            if image_field and not image_field.closed:
                thumb_field_name = f"{field_name}_thumb"
                if not self.make_thumbnail(image_field, thumb_field_name):
                    raise Exception(
                        f"Could not create thumbnail for {field_name} - is the file type valid?"
                    )
        
        # Mentsük újra a modellt a generált thumbnail-ekkel
        super().save(*args, **kwargs)

    def make_thumbnail(self, image_field, thumb_field_name):
        try:
            image = Image.open(image_field)

            orientation = None
            for key in ExifTags.TAGS.keys():
                if ExifTags.TAGS[key] == 'Orientation':
                    orientation = key
                    break

            # EXIF adatokat lekéred és ellenőrzöd, hogy van-e orientáció
            try:
                exif = dict(image._getexif().items())
                orientation_value = exif.get(orientation)  # Biztonságos hozzáférés
            except AttributeError:
                exif = None
                orientation_value = None
                
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
            
            image.thumbnail((1000, 1000), Image.BICUBIC)

            thumb_name, thumb_extension = os.path.splitext(os.path.basename(image_field.name))
            thumb_extension = thumb_extension.lower()
            thumb_filename = thumb_name + "_thumb" + thumb_extension

            if thumb_extension in [".jpg", ".jpeg"]:
                FTYPE = "JPEG"
            elif thumb_extension == ".gif":
                FTYPE = "GIF"
            elif thumb_extension == ".png":
                FTYPE = "PNG"
            else:
                return False  # Unrecognized file type

            # Save thumbnail to in-memory file as BytesIO
            temp_thumb = BytesIO()
            image.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)
            print('idemegjovunk')
            if hasattr(self, thumb_field_name):
                thumb_field = getattr(self, thumb_field_name)
                thumb_field.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)

            temp_thumb.close()

            return True
        
        except Exception as e:
            return False

class Service(ImageHandlerMixin, models.Model):
    service_name = models.CharField(max_length=255, unique=True, verbose_name = "szolgáltatás neve")
    service_main_img = models.ImageField(upload_to='app_bettirelax/img/photos/', verbose_name="főkép")
    service_main_img_thumb = models.ImageField(upload_to='app_bettirelax/img/thumbs/', blank=True, null=True, editable=False)
    service_secondary_img = models.ImageField(upload_to='app_bettirelax/img/photos/', blank=True, null=True, verbose_name = "másodlagos kép")
    service_secondary_img_thumb = models.ImageField(upload_to='app_bettirelax/img/thumbs/', blank=True, null=True, editable=False)
    service_main_description = QuillField(verbose_name = "elsődleges leírás")
    service_secondary_description = QuillField(blank=True, null=True, verbose_name = "másodlagos leírás")
    IMAGE_FIELDS = ['service_main_img', 'service_secondary_img']

    slug = models.SlugField(unique=True, blank=True, editable=False)  # Egyedi slug mező

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.service_name)  # Automatikus slug generálás
        super().save(*args, **kwargs)


    def get_price_range(self):
        prices = self.prices.all().order_by('price')  # Árak növekvő sorrendben
        if not prices.exists():
            return "Nincs ár megadva"
        elif prices.count() == 1:
            return f"{self.format_price(prices.first().price)} Ft"  # Ha csak egy ár van
        else:
            return f"{self.format_price(prices.first().price)} Ft - {self.format_price(prices.last().price)} Ft"  # Range

    @staticmethod
    def format_price(value):
        """Ezres elválasztó pontokat rak az árba, és eltávolítja a tizedeseket."""
        return "{:,.0f}".format(value).replace(",", ".")
    
    def __str__(self):
        return self.service_name
    
    def get_absolute_url(self):
        return reverse('service', kwargs={'slug': self.slug})  # Cseréld ki a megfelelő URL nevét
    
    class Meta:
        verbose_name = 'Szolgáltatás'
        verbose_name_plural = 'Szolgáltatások'

class ServicePrice(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='prices')
    duration_minutes = models.PositiveIntegerField(verbose_name="időtartam (perc)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ár (Ft)")

    def __str__(self):
        return f"{self.duration_minutes} perc - {self.price} Ft for {self.service.service_name}"

    class Meta:
        verbose_name = 'Szolgáltatás ár'
        verbose_name_plural = 'Szolgáltatás árak'

class BlogPost(ImageHandlerMixin, models.Model):
    main_image = models.ImageField(upload_to='app_bettirelax/img/photos/')
    main_image_thumb = models.ImageField(upload_to='app_bettirelax/img/thumbs/', blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=200, default="Betti")
    title = models.CharField(max_length=200)
    extract = models.CharField(max_length=200)
    content = QuillField()
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, editable=False)
    IMAGE_FIELDS = ['main_image']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Automatikusan generáljuk a slugot a cím alapján
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Blogposzt'
        verbose_name_plural = 'Blogposztok'

class AboutMe(ImageHandlerMixin, models.Model):
    photo = models.ImageField(upload_to='app_bettirelax/img/photos/', verbose_name="bemutatkozó kép")
    photo_thumb = models.ImageField(upload_to='app_bettirelax/img/thumbs/', blank=True, null=True, editable=False)
    aboutme = QuillField(verbose_name="bemutatkozó szöveg")
    IMAGE_FIELDS = ['photo']

    def __str__(self):
        return "Rólam"
    
    class Meta:
        verbose_name = 'Rólam'
        verbose_name_plural = 'Rólam'


class Review(ImageHandlerMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name="név")
    stars = models.PositiveSmallIntegerField(verbose_name="csillagok száma")  # 1-től 5-ig terjedő érték
    description = models.TextField(verbose_name="értékelés szövege")
    photo = models.ImageField(upload_to='app_bettirelax/img/photos/', default='app_brandon_photography/img/photos/default.jpg')
    photo_tumb = models.ImageField(upload_to='app_bettirelax/img/thumbs/',  default='app_brandon_photography/img/photos/default.jpg', editable=False)

    def __str__(self):
        return f"{self.name} ({self.stars} stars)"

    class Meta:
        verbose_name = 'Értékelés'
        verbose_name_plural = 'Értékelések'

class Faq(models.Model):
    question = models.TextField(verbose_name="kérdés")
    answer = models.TextField(verbose_name="válasz")

    def __str__(self):
        return str(self.question)

    class Meta:
        verbose_name = 'Gyakori kérdések'
        verbose_name_plural = 'Gyakori kérdések'


class Contact(models.Model):
    email_address = models.CharField(max_length=50, default="", verbose_name="emailcím")
    address_city = models.CharField(max_length=50, default="", verbose_name="cím: város")
    address_street = models.CharField(max_length=50, default="", verbose_name="cím: utca, házszám")
    address_postal = models.CharField(max_length=50, default="", verbose_name="cím: irányítószám")
    address_county = models.CharField(max_length=50, default="", verbose_name="cím: megye")
    address_country = models.CharField(max_length=50, default="", verbose_name="cím: ország")
    address_link =models.TextField(max_length=500, default="", verbose_name="térkép link")
    facebook = models.CharField(max_length=150, default="", verbose_name="facebook")
    facebook_messenger = models.CharField(max_length=150, default="", verbose_name="facebook messenger")
    phone_number = models.CharField(max_length=50, default="", verbose_name="telefonszám")
    contact_text=QuillField(default='', verbose_name="kapcsolat szöveg")

    class Meta:
        verbose_name = 'Kapcsolat'
        verbose_name_plural = 'Kapcsolat'

    def __str__(self):
        return "Kapcsolat"
    
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

class SpecialOpeningHours(models.Model):
    date = models.DateField(unique=True, verbose_name="Dátum")
    start_time = models.TimeField(verbose_name="Nyitás")
    end_time = models.TimeField(verbose_name="Zárás")

    def __str__(self):
        return f"{self.date}: {self.start_time} - {self.end_time}"

    class Meta:
        verbose_name = "Egyedi nyitvatartás"
        verbose_name_plural = "Egyedi nyitvatartások"

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