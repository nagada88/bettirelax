from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import localtime
from django.core.management.base import BaseCommand
from app_booking.models import Booking, BookingSettings, EmailTemplate
from datetime import timedelta 

class Command(BaseCommand):
    help = "Automatikusan elutasítja a lejárt foglalásokat."

    def handle(self, *args, **kwargs):
        current_time = localtime(now())
        settings_obj = BookingSettings.objects.first()
        if not settings_obj:
            self.stdout.write("Nincs BookingSettings konfiguráció!")
            return

        auto_reject_hours = settings_obj.auto_reject_time
        expiration_threshold = current_time - timedelta(hours=auto_reject_hours)
        print(f"Expiration threshold: {expiration_threshold}, TZ: {expiration_threshold.tzinfo}")

        for booking in Booking.objects.all():
            print(f"ID: {booking.id}, Created at: {booking.created_at}, Status: '{booking.status}'")


        expired_bookings = Booking.objects.filter(status="pending", created_at__lte=expiration_threshold)
        if not expired_bookings.exists():
            self.stdout.write("Nincsenek lejárt foglalások.")
            return

        for booking in expired_bookings:
            booking.status = "cancelled"
            booking.save()

            self.stdout.write(f"Foglalás elutasítva: {booking.id} - {booking.customer_email}")