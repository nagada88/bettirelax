from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import OpeningHours, Booking, BookingSettings
from datetime import datetime, timedelta
from django.http import JsonResponse
from calendar import monthrange
from django.utils.timezone import localdate


def booking_view(request):
    """Foglalási naptár nézet, amely kezeli a hónapok közötti lapozást."""

    # 📅 Alapértelmezett dátum: aktuális hónap
    today = localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # 🔥 Foglalási beállítások lekérése
    booking_settings = BookingSettings.objects.first()
    max_weeks = booking_settings.max_weeks_in_advance if booking_settings else 4  # Ha nincs beállítás, 4 hetet engedélyezünk

    # 📅 Engedélyezett dátum limit számítása
    max_allowed_date = today + timedelta(weeks=max_weeks)

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

    # 🚀 Nyitvatartások lekérése és foglalások ellenőrzése
    for day in range(1, days_in_month + 1):
        current_date = datetime(year, month, day).date()
        day_of_week = current_date.weekday()
        is_even_week = (current_date.isocalendar()[1] % 2) == 0

        if current_date > max_allowed_date:
            status = "grey"
        else:
            # 📅 Megnézzük, hogy van-e nyitvatartás
            opening_hours = OpeningHours.objects.filter(day_of_week=day_of_week, is_even_week=is_even_week)
            available_slots = []

            for opening in opening_hours:
                current_slot = opening.start_time
                while current_slot < opening.end_time:
                    end_slot = (datetime.combine(current_date, current_slot) + timedelta(minutes=15)).time()
                    
                    # ✅ Ellenőrizzük, hogy a slot foglalt-e
                    is_taken = Booking.objects.filter(date=current_date, start_time=current_slot).exists()
                    
                    if not is_taken:
                        available_slots.append(current_slot)

                    current_slot = end_slot  # ⏩ Következő 15 perces slot

            # 📅 Zöld: van elérhető időpont, Piros: nincs szabad hely
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
    available_slots = []

    # Lekérjük az adott napi nyitvatartásokat
    opening_hours = OpeningHours.objects.filter(day_of_week=day_of_week, is_even_week=is_even_week)
    bookings = Booking.objects.filter(date=selected_date)

    for opening in opening_hours:
        current_slot = opening.start_time
        while current_slot < opening.end_time:
            end_slot = (datetime.combine(selected_date, current_slot) + timedelta(minutes=15)).time()

            # Foglaltság ellenőrzése
            is_taken = bookings.filter(start_time=current_slot).exists()
            if not is_taken:
                available_slots.append(current_slot.strftime("%H:%M"))

            current_slot = end_slot

    return JsonResponse({"available_slots": available_slots})


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