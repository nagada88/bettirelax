from django.shortcuts import render
from .models import *

# Create your views here.

def introduction(request):
    # pictures = Photos.objects.filter(category__name="kutyafotózás")
    # studiopictures = Photos.objects.filter(category__name="studio")
    # reviews = load_more_reviews(request)
    aboutme = AboutMe.objects.get(id=1)
    services = Service.objects.all()
    context={'aboutme': aboutme, 'services': services}

    return render(request, 'introduction.html', context)

def service(request):
    return render(request, 'service.html')

def pricelist(request):
    return render(request, 'pricelist.html')

def faq(request):
    faqs = Faq.objects.all()
    return render(request, 'faq.html', {'faqs': faqs})

def bloglist(request):
    return render(request, 'bloglist.html')



