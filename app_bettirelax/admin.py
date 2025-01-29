from django.contrib import admin
from .models import *

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

# Register your models here.
admin.site.register(BlogPost)
admin.site.register(AboutMe, AboutMeAdmin)
admin.site.register(Faq)
admin.site.register(Review)