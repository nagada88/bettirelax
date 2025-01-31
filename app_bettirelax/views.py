from django.shortcuts import render
from .models import *

# Create your views here.

def introduction(request):
    aboutme = AboutMe.objects.first() 
    contact = Contact.objects.first() 
    services = Service.objects.all()
    context={'aboutme': aboutme, 'services': services, 'contact': contact}

    return render(request, 'introduction.html', context)

def service(request, slug):
    service = get_object_or_404(Service, slug=slug)
    services = Service.objects.all()
    contact = Contact.objects.first() 
    context = {'service': service, 'services': services, 'contact': contact}

    return render(request, 'service.html', context)

def pricelist(request):
    services = Service.objects.prefetch_related('prices').all()  
    contact = Contact.objects.first() 
    context = {'services': services, 'contact': contact}
               
    return render(request, 'pricelist.html', context)

def faq(request):
    faqs = Faq.objects.all()
    aboutme = AboutMe.objects.first() 
    services = Service.objects.all()
    contact = Contact.objects.first() 
    context = {'faqs': faqs, 'services': services, 'contact': contact, 'aboutme': aboutme}

    return render(request, 'faq.html', context)

def bloglist(request):
    services = Service.objects.all()
    bloglist = BlogPost.objects.all()
    contact = Contact.objects.first() 
    context = {'services': services, 'bloglist': bloglist, 'contact': contact}

    return render(request, 'bloglist.html', context)

def blogpost(request, slug):
    services = Service.objects.all()
    contact = Contact.objects.first() 
    context = {'blogpost': blogpost, 'services': services, 'contact': contact}

    return render(request, 'blogpost.html', context)



