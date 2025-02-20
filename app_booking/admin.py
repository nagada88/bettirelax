from django.contrib import admin
from .models import OpeningHours, BookingSettings, Booking, EmailTemplate
from django import forms
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
import datetime
from django.utils.timezone import now

# "Foglalási rendszer" címkével ellátott szekció létrehozása az adminban
admin.site.site_header = "Foglalási rendszer"
admin.site.index_title = "Foglalási rendszer adminisztráció"
admin.site.site_title = "Foglalási rendszer admin"

class FutureBookingFilter(admin.SimpleListFilter):
    title = "Jövőbeli foglalások"  # Szűrő neve az admin felületen
    parameter_name = "future_bookings"

    def lookups(self, request, model_admin):
        return [
            ("upcoming", "Jövőbeli foglalások"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "upcoming":
            return queryset.filter(date__gte=now().date())  # 🔥 Csak a jövőbeli foglalásokat szűri
        return queryset

class InstanceCounterMixin1():
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


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
        
    def clean(self):
        """Validálja, hogy a kezdési időpont korábban legyen a zárásnál."""
        cleaned_data = super().clean()
        errors = {}

        for day, label in self.DAYS:
            start_even = cleaned_data.get(f"start_even_{day}")
            end_even = cleaned_data.get(f"end_even_{day}")
            start_odd = cleaned_data.get(f"start_odd_{day}")
            end_odd = cleaned_data.get(f"end_odd_{day}")

            if start_even and end_even and start_even >= end_even:
                errors[f"start_even_{day}"] = f"A nyitás nem lehet később vagy ugyanakkor, mint a zárás!"
                errors[f"end_even_{day}"] = f"A zárás nem lehet korábban vagy ugyanakkor, mint a nyitás"
            if start_even and not end_even:
                errors[f"end_even_{day}"] = f"Kérlek a zárási időpontot is tölsd ki!"           
            if end_even and not start_even:
                errors[f"start_even_{day}"] = f"Kérlek a nyitási időpontot is tölsd ki!"

            if start_odd and end_odd and start_odd >= end_odd:
                errors[f"start_odd_{day}"] = f"A nyitás nem lehet később vagy ugyanakkor, mint a zárás!"
                errors[f"end_odd_{day}"] = f"A zárás nem lehet korábban vagy ugyanakkor, mint a nyitás"
            if start_odd and not end_odd:
                errors[f"end_odd_{day}"] = f"Kérlek a zárási időpontot is tölsd ki!"                
            if end_odd and not start_odd:
                errors[f"start_odd_{day}"] = f"Kérlek a nyitási időpontot is tölsd ki!"
                
        if errors:
            for key, value in errors.items():
                self.add_error(key, value)  # 🔥 Hibaüzenetek hozzárendelése a mezőkhöz
            raise forms.ValidationError("Kérlek javítsd a fenti hibákat!")

        return cleaned_data

class OpeningHoursAdmin(admin.ModelAdmin):
    """Egyedi admin nézet a nyitvatartási idők beállítására"""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("custom/", self.admin_site.admin_view(self.custom_view), name="custom_opening_hours"),  # 🔥 Itt nevezzük el helyesen!
        ]
        return custom_urls + urls

    def custom_view(self, request):
        """Egyedi admin oldal a nyitvatartás kezelésére"""

        initial_data = {}
        for entry in OpeningHours.objects.all():
            key_prefix = "even" if entry.is_even_week else "odd"
            initial_data[f"start_{key_prefix}_{entry.day_of_week}"] = entry.start_time.strftime("%H:%M") 
            initial_data[f"end_{key_prefix}_{entry.day_of_week}"] = entry.end_time.strftime("%H:%M")

        if request.method == "POST":
            form = CustomOpeningHoursForm(request.POST, initial=initial_data)
            if form.is_valid():
                # 🔥 2️⃣ Adatok mentése az adatbázisba
                OpeningHours.objects.all().delete()
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

                return HttpResponseRedirect(reverse("admin:index"))  # 🔥 Mentés után vissza az adminba
            
            else:
                # 🔥 Ha a form nem valid, akkor adjuk vissza az eddigi adatokat (ne törlődjenek el)
                for day, _ in form.DAYS:
                    for key_prefix in ["start_even_", "end_even_", "start_odd_", "end_odd_"]:
                        field_key = f"{key_prefix}{day}"
                        if field_key in request.POST:
                            initial_data[field_key] = request.POST[field_key]

        else:
            form = CustomOpeningHoursForm(initial=initial_data)

        return render(request, "admin/custom_opening_hours.html", {"form": form, "opts": self.model._meta})


    def changelist_view(self, request, extra_context=None):
        """Amikor a felhasználó a Nyitvatartások admin linkre kattint, automatikusan a custom szerkesztő oldalra irányítjuk."""
        return HttpResponseRedirect(reverse("admin:custom_opening_hours"))

@admin.register(BookingSettings)
class BookingSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Általános beállítások", {
            "fields": ("is_booking_enabled", "max_weeks_in_advance", "min_hours_before_booking", "auto_reject_time", "booking_puffer")
        }),
        ("Foglalási dokumentumok", {
            "fields": ("terms_conditions_pdf", "contraindications_pdf", "privacy_policy_pdf")
        }),
    )

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("type",)
    search_fields = ("type",)
    
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "date", "start_time", "status")  # Megjelenő oszlopok
    list_filter = ("status", FutureBookingFilter)  # 🔥 Szűrés státusz + jövőbeli foglalások

# Regisztráljuk a custom admin nézetet
admin.site.register(OpeningHours, OpeningHoursAdmin)
# admin.site.register(BookingSettings, BookingSettingsAdmin)


