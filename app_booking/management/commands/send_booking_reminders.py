from django.core.management.base import BaseCommand
from django.utils.timezone import now, localtime
from django.core.mail import send_mail
from django.conf import settings
from app_booking.models import Booking, EmailTemplate
import re
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = "Küldjön emlékeztető e-mailt az aznapi foglalásokhoz egy adott időpont után."

    def handle(self, *args, **kwargs):

        # Az aktuális idő beolvasása
        current_time = localtime(now())

        today = current_time.date()

        # Lekérdezzük az aznapi elfogadott foglalásokat
        bookings = Booking.objects.filter(status="accepted", date=today)
        if not bookings.exists():
            self.stdout.write("Nincsenek emlékeztetendő foglalások ma.")
            return

        # Lekérdezzük az emlékeztető email sablont
        try:
            template = EmailTemplate.objects.get(type="reminder")
            email_body = template.content.html

            # HTML tagek helyettesítése új sorokkal
            email_body = re.sub(r'<br\s*/?>', '\n', email_body)  # <br> → új sor
            email_body = re.sub(r'</p>', '\n', email_body)  # </p> → új sor
            email_body = strip_tags(email_body).strip()  # Eltávolítjuk a maradék HTML-t
        except EmailTemplate.DoesNotExist:
            email_body = "Tisztelt ügyfelünk,\n\nNe feledje, hogy ma van a foglalása!"


        # Emailek kiküldése
        for booking in bookings:
            # Foglalás adatai blokk
            booking_details = (
                f"\n\nFoglalás adatai:\n"
                f"Időpont: {booking.date} {booking.start_time.strftime('%H:%M')}\n"
                f"Szolgáltatás: {booking.booked_service_type}\n"
                f"Név: {booking.customer_name}\n"
            )

            # Email teljes tartalmának összeállítása
            message = email_body + booking_details

            subject = "Emlékeztető: mai foglalásod - Betti Relax"

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [booking.customer_email],
                fail_silently=False,
            )

            self.stdout.write(f"Emlékeztető elküldve: {booking.customer_email}")

