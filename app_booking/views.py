from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import OpeningHours, Booking, BookingSettings
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from calendar import monthrange
from django.utils.timezone import localdate
from app_bettirelax.models import Service, ServicePrice
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import localdate
from calendar import monthrange
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse

MONTHS_HU = {
    1: "január",
    2: "február",
    3: "március",
    4: "április",
    5: "május",
    6: "június",
    7: "július",
    8: "augusztus",
    9: "szeptember",
    10: "október",
    11: "november",
    12: "december",
}

def booking_view(request):
    """Foglalási naptár nézet, amely kezeli a hónapok közötti lapozást."""

    # 📅 Alapértelmezett dátum: aktuális hónap
    today = localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))
    month_name = MONTHS_HU[month]  # Itt történik az átalakítás

    # 🔥 Foglalási beállítások lekérése
    booking_settings = BookingSettings.objects.first()
    max_weeks = booking_settings.max_weeks_in_advance if booking_settings else 4  # Ha nincs beállítás, 4 hetet engedélyezünk
    puffer_minutes = int(booking_settings.booking_puffer) if booking_settings else 0  # Puffer idő
    min_hours_before_booking = booking_settings.min_hours_before_booking if booking_settings else 24

    # 📅 Engedélyezett dátum limit számítása
    max_allowed_date = today + timedelta(weeks=max_weeks)

    # 🕒 Minimális foglalható időpont
    now = datetime.now()
    min_allowed_datetime = now + timedelta(hours=min_hours_before_booking)

    # 📅 Hónap előző/következő navigációs változók
    prev_month = month - 1 if month > 1 else 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    # 📅 Napok számának lekérése az adott hónapra
    days_in_month = monthrange(year, month)[1]

    # 📅 Hónap első napja és hétkezdő nap kiszámítása
    first_day = datetime(year, month, 1).date()
    first_day_of_week = first_day.weekday()  # 0 = Hétfő, 6 = Vasárnap

    # 📅 Heti napok sorrendje
    days_of_week = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]

    # 📅 Hónap adatok inicializálása
    calendar_data = []
    week = []

    # 📅 Üres cellák a hónap elején, ha az első nap nem hétfő
    for _ in range(first_day_of_week):
        week.append({"date": None, "status": "empty"})

    # ⏳ Legrövidebb szolgáltatás hossza percekben
    min_service = ServicePrice.objects.order_by("duration_minutes").first()
    min_service_duration = min_service.duration_minutes if min_service else 15  # Alapértelmezés 15 perc

    # 🚀 Nyitvatartások lekérése és foglalások ellenőrzése
    for day in range(1, days_in_month + 1):
        current_date = datetime(year, month, day).date()
        day_of_week = current_date.weekday()
        is_even_week = (current_date.isocalendar()[1] % 2) == 0

        # 🛑 Ha a nap már elmúlt vagy túl van a foglalható időn, legyen unavailable
        if current_date < today or current_date > max_allowed_date:
            status = "grey"
        else:
            # 📅 Nyitvatartásokat lekérjük
            opening_hours = OpeningHours.objects.filter(day_of_week=day_of_week, is_even_week=is_even_week)
            available_slots = []

            # 🔍 Foglalt időpontok összegyűjtése
            taken_slots = []
            for booking in Booking.objects.filter(date=current_date, status__in=["pending", "accepted"]):
                booking_duration = booking.booked_service_length
                booking_end_time = (datetime.combine(current_date, booking.start_time) + timedelta(minutes=booking_duration + puffer_minutes)).time()
                taken_slots.append((booking.start_time, booking_end_time))

            # 📌 Nyitvatartási időpontok bejárása
            for opening in opening_hours:
                # ⏳ Kezdőidő kerekítése a legközelebbi félórás pontra
                start_hour = opening.start_time.hour
                start_minute = opening.start_time.minute

                if start_minute > 0 and start_minute < 30:
                    start_minute = 30
                elif start_minute > 30:
                    start_hour += 1
                    start_minute = 0

                current_time = datetime.combine(current_date, time(start_hour, start_minute))  # Kerekített kezdőidő
                end_time = datetime.combine(current_date, opening.end_time)

                while current_time.time() < end_time.time():
                    next_time = current_time + timedelta(minutes=min_service_duration)

                    # ❌ Foglaltság ellenőrzése
                    conflict = any(start <= current_time.time() < end for start, end in taken_slots)

                    if current_time >= min_allowed_datetime and not conflict and next_time.time() <= end_time.time():
                        available_slots.append(current_time.time())

                    # ⏩ Következő slotra lépünk
                    current_time = next_time

            # 📅 Ha a kerekítés miatt nincs szabad időpont → szürkére állítjuk a napot
            if not available_slots:
                status = "grey"
            else:
                status = "green" if any(available_slots) else "red"

        week.append({"date": current_date, "status": status})


        # 🌎 Ha a hét végére értünk, új sort kezdünk
        if len(week) == 7:
            calendar_data.append(week)
            week = []

    # 📅 Ha a hónap nem teljes héttel végződik, az utolsó sort is hozzáadjuk, üres cellákkal
    if week:
        while len(week) < 7:
            week.append({"date": None, "status": "empty"})
        calendar_data.append(week)

    # 🔄 Kontextus a template-nek
    context = {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "days_of_week": days_of_week,
        "calendar_data": calendar_data,
        "today": today,
        "month_name": month_name,
    }

    return render(request, "booking.html", context)

def get_available_slots(request):
    """AJAX kérés kiszolgálása az elérhető időpontokra"""
    
    date_str = request.GET.get("date")
    if not date_str:
        return JsonResponse({"error": "No date provided"}, status=400)

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    day_of_week = selected_date.weekday()
    is_even_week = (selected_date.isocalendar()[1] % 2) == 0

    # ⏳ Legrövidebb szolgáltatás hossza percekben
    min_service = ServicePrice.objects.order_by("duration_minutes").first()
    if not min_service:
        return JsonResponse({"success": False, "error": "Nincsenek szolgáltatások!"})
    
    min_service_duration = min_service.duration_minutes

    # 🕒 Puffer idő lekérése
    booking_settings = BookingSettings.objects.first()
    puffer_minutes = int(booking_settings.booking_puffer) if booking_settings else 0
    min_hours_before_booking = booking_settings.min_hours_before_booking if booking_settings else 24

    # ⏳ Minimális foglalható időpont kiszámítása
    now = datetime.now()
    min_allowed_datetime = now + timedelta(hours=min_hours_before_booking)
                                           
    available_slots = []

    # 📅 Nyitvatartási időpontok lekérése
    opening_hours = OpeningHours.objects.filter(day_of_week=day_of_week, is_even_week=is_even_week)

    # 🔍 Foglalt időpontok előre lekérdezése és gyors elérhetővé tétele
    taken_slots = []
    for booking in Booking.objects.filter(date=selected_date, status__in=["pending", "accepted"]):
        booking_duration = booking.booked_service_length
        booking_end_time = (datetime.combine(selected_date, booking.start_time) + timedelta(minutes=booking_duration + puffer_minutes)).time()
        taken_slots.append((booking.start_time, booking_end_time))

    for opening in opening_hours:
        # ⏳ Kezdőidő kerekítése a legközelebbi félórás pontra
        start_hour = opening.start_time.hour
        start_minute = opening.start_time.minute

        # Ha 1-29 perc között van, akkor félre kerekítjük (például 08:10 → 08:30)
        # Ha 31-59 perc között van, akkor a következő órára kerekítjük (például 08:40 → 09:00)
        if start_minute > 0 and start_minute < 30:
            start_minute = 30
        elif start_minute > 30:
            start_hour += 1
            start_minute = 0

        current_time = datetime.combine(selected_date, time(start_hour, start_minute))  # Kerekített kezdőidő
        end_time = datetime.combine(selected_date, opening.end_time)

        while current_time.time() < end_time.time():
            next_time = current_time + timedelta(minutes=min_service_duration)

            # ❌ Foglaltság ellenőrzése
            conflict = any(start <= current_time.time() < end for start, end in taken_slots)

            if current_time >= min_allowed_datetime and not conflict and next_time.time() <= end_time.time():
                available_slots.append(current_time.time().strftime("%H:%M"))

            # ⏩ Következő időpontra lépés
            current_time = next_time

    return JsonResponse({"available_slots": available_slots})


def get_available_services(request):
    """Visszaadja a kiválasztott időponttól elérhető szolgáltatásokat."""
    selected_date = request.GET.get("date")  # Pl. "2025-02-10"
    selected_time = request.GET.get("time")  # Pl. "10:30"

    if not selected_date or not selected_time:
        return JsonResponse({"success": False, "error": "Dátum és időpont szükséges!"})

    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        selected_time = datetime.strptime(selected_time, "%H:%M").time()
    except ValueError:
        return JsonResponse({"success": False, "error": "Hibás dátum/idő formátum!"})

    # 📅 A kiválasztott időpontot datetime objektummá alakítjuk
    start_datetime = datetime.combine(selected_date, selected_time)

    # ⏳ Kiszámoljuk a következő "not available" időpontot
    # (zárás, másik foglalás, vagy a max_weeks_in_advance miatt tiltott időpont)
    next_not_available = None

    # 🔎 Megnézzük a nyitvatartást az adott napra
    day_of_week = selected_date.weekday()
    is_even_week = (selected_date.isocalendar()[1] % 2) == 0
    opening_hours = OpeningHours.objects.filter(day_of_week=day_of_week, is_even_week=is_even_week)

    for opening in opening_hours:
        if opening.start_time <= selected_time < opening.end_time:
            if not next_not_available or opening.end_time < next_not_available:
                next_not_available = opening.end_time

    # 🔎 Megnézzük a már meglévő foglalásokat
    existing_bookings = Booking.objects.filter(date=selected_date, start_time__gte=selected_time, status__in=["pending", "accepted"]).order_by("start_time")
    for booking in existing_bookings:
        if not next_not_available or booking.start_time < next_not_available:
            next_not_available = booking.start_time

    if not next_not_available:
        return JsonResponse({"success": False, "error": "Nem található elérhető időszak!"})

    # ⏳ Szabad időintervallum hossza percekben
    free_minutes = int((datetime.combine(selected_date, next_not_available) - start_datetime).total_seconds() / 60)

    # 🎯 Megnézzük, mely szolgáltatások férnek bele
    available_services = []
    for service in Service.objects.all():
        for price in service.prices.all():
            if price.duration_minutes <= free_minutes:
                available_services.append({
                    "service_id": service.id,
                    "service_name": service.service_name,
                    "duration": price.duration_minutes,
                    "price": price.price
                })

    return JsonResponse({"success": True, "available_services": available_services})





@login_required
def admin_create_booking(request):
    """🔒 Csak adminok tudnak extra időpontokat foglalni a rendszerben."""
    if not request.user.is_staff:
        return redirect("booking_view")  # 🔄 Ha nem admin, visszairányítjuk

    if request.method == "POST":
        day_of_week = int(request.POST.get("day_of_week"))
        is_even_week = request.POST.get("is_even_week") == "True"
        start_time_str = request.POST.get("start_time")
        block_duration = int(request.POST.get("block_duration"))  # ⏳ Időtartam (pl. 15 vagy 30 perc)

        # 🕒 Idő számítása
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=block_duration)).time()

        # ✅ Foglalás mentése adminként
        Booking.objects.create(
            user=request.user,  # 👤 Admin foglal
            day_of_week=day_of_week,
            is_even_week=is_even_week,
            start_time=start_time,
            end_time=end_time,
            status="accepted"  # 🚀 Elfogadottként menti
        )

    return redirect("booking_view")  # 🔄 Vissza az időpontfoglalásra

def booking_details_view(request):
    """Foglalási adatok megadása nézet"""
    selected_date = request.GET.get("date")
    selected_time = request.GET.get("time")
    service_id = request.GET.get("service_id")
    duration = request.GET.get("duration")
    service = Service.objects.get(id=service_id)
    settings_obj = BookingSettings.objects.first()
    
    # Ellenőrzés
    if not all([selected_date, selected_time, service_id, duration]):
        return JsonResponse({"error": "Hiányzó adatok a foglaláshoz!"}, status=400)
    
    if not selected_date or not selected_time or not service_id:
        return render(request, "error.html", {"message": "Hiányzó adatok a foglaláshoz!"})

    context = {
        "selected_date": selected_date,
        "selected_time": selected_time,
        "service": service,
        "duration": duration,
        "terms_conditions_pdf": settings_obj.terms_conditions_pdf.url if settings_obj and settings_obj.terms_conditions_pdf else None,
        "contraindications_pdf": settings_obj.contraindications_pdf.url if settings_obj and settings_obj.contraindications_pdf else None,
        "privacy_policy_pdf": settings_obj.privacy_policy_pdf.url if settings_obj and settings_obj.privacy_policy_pdf else None,
          
    }
    return render(request, "booking_details.html", context)



def submit_booking(request):
    if request.method == "POST":
        start_time_str = request.POST.get("time")
        start_time = datetime.strptime(start_time_str, "%H:%M").time()  # Konvertáljuk `time` típusra
        start_date = request.POST.get("date")
        service_type = Service.objects.get(id=request.POST.get("service_id")).service_name

        customer_name = request.POST.get("customer_name")
        customer_email = request.POST.get("customer_email")
        customer_phone = request.POST.get("customer_phone")
        
        billing_name = request.POST.get("billing_name")
        billing_tax_number = request.POST.get("billing_tax_number", "")  # Nem kötelező mező
        billing_zip = request.POST.get("billing_zip")
        billing_city = request.POST.get("billing_city")
        billing_address = request.POST.get("billing_address")

        # Kötelező checkboxok ellenőrzése
        privacy_policy = request.POST.get("privacy_policy")
        terms_conditions = request.POST.get("terms_conditions")
        contraindications = request.POST.get("contraindications")
        newsletter = request.POST.get("newsletter", False)  # Nem kötelező, alapból False

        if not all([customer_name, customer_email, customer_phone, billing_name, billing_zip, billing_city, billing_address, privacy_policy, terms_conditions, contraindications]):
            messages.error(request, "Minden kötelező mezőt ki kell tölteni és el kell fogadni az összes kötelező hozzájárulást.")
            return redirect("booking_details")

        admin_token = get_random_string(length=32)

        booking = Booking.objects.create(
            start_time=start_time,
            date=start_date,
            booked_service_type=service_type,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            billing_name=billing_name,
            billing_tax_number=billing_tax_number,
            billing_zip=billing_zip,
            billing_city=billing_city,
            billing_address=billing_address,
            status="pending",
            admin_token=admin_token  # 🔑 Token közvetlen mentése
        )

        # Egyedi token generálása az admin műveletekhez
        booking.admin_token = admin_token
        booking.save()

        # Email küldése Bettinek
        admin_url = request.build_absolute_uri(reverse('confirm_booking', args=[booking.id, admin_token]))
        send_mail(
            subject="Új foglalási igény érkezett",
            message=(
                f"Új foglalás érkezett: \n"
                f"Név: {customer_name}\n"
                f"Időpont: {start_date} {start_time}\n"
                f"Szolgáltatás: {service_type}\n"
                f"Foglalási link elfogadáshoz: {admin_url}\n"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["brandbehozunk@gmail.com"],
            fail_silently=False,
        )
        
        return redirect("booking_success") 

    return render(request, "booking_details.html")

def booking_success(request):
    return render(request, "booking_success.html")



def confirm_booking(request, booking_id, token):
    """Admin URL alapján foglalás elfogadása."""
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.admin_token != token:
        return HttpResponse("Hibás token!", status=403)

    # Foglalás státuszának frissítése
    booking.status = "accepted"
    booking.save()

    return HttpResponse("Foglalás elfogadva és email küldve a vevőnek!")

