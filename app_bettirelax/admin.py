from django.contrib import admin
from .models import *
from .models import OpeningHours, SpecialOpeningHours, BookingSettings
from django import forms
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import render, redirect

# "Foglalási rendszer" címkével ellátott szekció létrehozása az adminban
admin.site.site_header = "Foglalási rendszer"
admin.site.index_title = "Foglalási rendszer adminisztráció"
admin.site.site_title = "Foglalási rendszer admin"


from django.contrib import admin
from .models import OpeningHours, SpecialOpeningHours, BookingSettings

# Új szekció definiálása
class BookingSystemAdminSite(admin.AdminSite):
    site_header = "Foglalási rendszer"
    site_title = "Foglalási rendszer admin"
    index_title = "Foglalási rendszer kezelése"

# Példányosítjuk az új admin oldalt
booking_admin = BookingSystemAdminSite(name="booking_admin")

class CustomOpeningHoursForm(forms.Form):
    """Form az egyedi admin szerkesztő nézethez, 24 órás időformátummal"""
    DAYS = [
        (0, 'Hétfő'),
        (1, 'Kedd'),
        (2, 'Szerda'),
        (3, 'Csütörtök'),
        (4, 'Péntek'),
        (5, 'Szombat'),
        (6, 'Vasárnap'),
    ]

    time_format = "%H:%M"  # 24 órás időformátum

    for day in DAYS:
        locals()[f"start_even_{day[0]}"] = forms.TimeField(
            required=False, label=f"{day[1]} (Páros hét) - Nyitás",
            widget=forms.TimeInput(format=time_format, attrs={'class': 'timepicker'}))
        locals()[f"end_even_{day[0]}"] = forms.TimeField(
            required=False, label=f"{day[1]} (Páros hét) - Zárás",
            widget=forms.TimeInput(format=time_format, attrs={'class': 'timepicker'}))
        locals()[f"start_odd_{day[0]}"] = forms.TimeField(
            required=False, label=f"{day[1]} (Páratlan hét) - Nyitás",
            widget=forms.TimeInput(format=time_format, attrs={'class': 'timepicker'}))
        locals()[f"end_odd_{day[0]}"] = forms.TimeField(
            required=False, label=f"{day[1]} (Páratlan hét) - Zárás",
            widget=forms.TimeInput(format=time_format, attrs={'class': 'timepicker'}))


class OpeningHoursAdmin(admin.ModelAdmin):
    """Egyedi admin nézet a nyitvatartási idők beállítására"""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom/', self.admin_site.admin_view(self.custom_view), name="custom_opening_hours"),
        ]
        return custom_urls + urls

    def custom_view(self, request):
        """Egyedi admin oldal a nyitvatartás kezelésére"""
        if request.method == "POST":
            form = CustomOpeningHoursForm(request.POST)
            if form.is_valid():
                # Töröljük az összes nyitvatartási rekordot
                OpeningHours.objects.all().delete()

                # Mentjük az új beállításokat
                for day, _ in form.DAYS:
                    start_even = form.cleaned_data.get(f"start_even_{day}")
                    end_even = form.cleaned_data.get(f"end_even_{day}")
                    start_odd = form.cleaned_data.get(f"start_odd_{day}")
                    end_odd = form.cleaned_data.get(f"end_odd_{day}")

                    if start_even and end_even:
                        OpeningHours.objects.create(
                            day_of_week=day, is_even_week=True, start_time=start_even, end_time=end_even)
                    if start_odd and end_odd:
                        OpeningHours.objects.create(
                            day_of_week=day, is_even_week=False, start_time=start_odd, end_time=end_odd)

                return HttpResponseRedirect(request.path)

        else:
            # Betöltjük a meglévő adatokat
            initial_data = {}
            for entry in OpeningHours.objects.all():
                key_prefix = "even" if entry.is_even_week else "odd"
                initial_data[f"start_{key_prefix}_{entry.day_of_week}"] = entry.start_time
                initial_data[f"end_{key_prefix}_{entry.day_of_week}"] = entry.end_time

            form = CustomOpeningHoursForm(initial=initial_data)

        return render(request, "admin/custom_opening_hours.html", {"form": form, "opts": self.model._meta})

# Regisztráljuk a custom admin nézetet
admin.site.register(OpeningHours, OpeningHoursAdmin)

class SpecialOpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time')
    list_filter = ('date',)
    ordering = ('date',)

    class Meta:
        verbose_name = "Egyedi nyitvatartás"
        verbose_name_plural = "Egyedi nyitvatartások"

class BookingSettingsAdmin(admin.ModelAdmin):
    list_display = ('is_booking_enabled', 'max_weeks_in_advance', 'min_hours_before_booking', 'auto_reject_time')
    list_display_links = ('is_booking_enabled',)  # Kattinthatóvá tesszük az első mezőt
    list_editable = ('max_weeks_in_advance', 'min_hours_before_booking', 'auto_reject_time')


    class Meta:
        verbose_name = "Foglalási beállítások"
        verbose_name_plural = "Foglalási beállítások"


# Regisztráljuk a modelleket ebben az új admin oldalban
booking_admin.register(OpeningHours, OpeningHoursAdmin)
booking_admin.register(SpecialOpeningHours, SpecialOpeningHoursAdmin)
booking_admin.register(BookingSettings, BookingSettingsAdmin)


class InstanceCounterMixin1():
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True

class ServicePriceInline(admin.TabularInline):  # TabularInline megjelenítés
    model = ServicePrice
    extra = 1  # Hány üres sor jelenjen meg új ServicePrice-hoz
    min_num = 1  # Minimum ár hozzárendelése
    max_num = 10  # Maximum ár hozzárendelése (opcionális)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name',)
    inlines = [ServicePriceInline]  # Inline kapcsolás

class AboutMeAdmin(InstanceCounterMixin1, admin.ModelAdmin):
    model = AboutMe

class ContactAdmin(InstanceCounterMixin1, admin.ModelAdmin):
    model = Contact

# Register your models here.
admin.site.register(BlogPost)
admin.site.register(AboutMe, AboutMeAdmin)
admin.site.register(Faq)
admin.site.register(Review)
admin.site.register(Contact, ContactAdmin)