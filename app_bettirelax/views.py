from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from cookie_consent.util import get_cookie_value_from_request
from cookie_consent.models import CookieGroup
from django.shortcuts import redirect

def cookie_banner_context(request):
    """
    Globális context processor, amely az összes cookie groupot elküldi a template-be.
    """
    return {"cookie_groups": CookieGroup.objects.all()}

def cookie_status(request):
    """
    Ellenőrzi a cookie-k állapotát, és visszaküldi JSON formátumban.
    """
    print(f"🔍 Beérkező sütik: {request.COOKIES}")  # 🔹 Debug log

    cookie_groups = CookieGroup.objects.all()
    
    cookie_status = {}
    for group in cookie_groups:
        cookie_name = f"cookie_consent_{group.varname}"
        cookie_value = request.COOKIES.get(cookie_name)  # 🔹 Olvassuk ki a sütit

        if cookie_value is None:
            print(f"⚠️ Süti {cookie_name} HIÁNYZIK, banner kell!")  # Debug log
            is_accepted = None
        else:
            is_accepted = cookie_value == "accepted"

        cookie_status[group.varname] = {
            "accepted": is_accepted,
            "scripts": []
        }

        # 🔹 Ha az analytics süti ELFOGADOTT, akkor adjuk hozzá a GA4 scriptet
        if group.varname == "analytics" and is_accepted:
            print(f"✅ Süti {cookie_name} engedélyezett, betöltjük a Google Tag Managert!")  # Debug log
            cookie_status[group.varname]["scripts"].append(
                '<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASURE_ID"></script>'
                '<script>window.dataLayer = window.dataLayer || []; '
                'function gtag(){dataLayer.push(arguments);} '
                'gtag("js", new Date()); '
                'gtag("config", "GA_MEASURE_ID");</script>'
            )

    print(f"📩 Visszaküldött JSON: {cookie_status}")  # 🔹 Debug log

    return JsonResponse(cookie_status)


from django.http import JsonResponse

def accept_cookie_group(request, group_name):
    """
    Elfogadja az adott cookie csoportot, és visszaküldi a szükséges scriptet.
    """
    cookie_group = CookieGroup.objects.filter(varname=group_name).first()
    if not cookie_group:
        return JsonResponse({"error": "Invalid cookie group"}, status=400)

    response_data = {
        "status": "accepted",
        "scripts": []
    }

    # 🔹 Hozzuk létre a JSON választ külön
    response = JsonResponse(response_data)

    # 🔹 Kényszerítsük ki a sütibeállítást
    cookie_name = f"cookie_consent_{group_name}"
    response.set_cookie(
        cookie_name,
        "accepted",
        max_age=365*24*60*60,
        path="/",
        secure=False,  # Ha HTTPS-en fut, állítsd True-ra!
        httponly=False,  # Ha True, akkor JS nem tudja olvasni
        samesite="Lax"
    )

    print(f"📩 Set-Cookie küldve: {cookie_name}=accepted")  # 🔹 Debug log

    if group_name == "analytics":
        response_data["scripts"].append(
            '<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASURE_ID"></script>'
            '<script>window.dataLayer = window.dataLayer || []; '
            'function gtag(){dataLayer.push(arguments);} '
            'gtag("js", new Date()); '
            'gtag("config", "GA_MEASURE_ID");</script>'
        )
        response = JsonResponse(response_data)

        # 🔹 Itt is KÉNYSZERÍTJÜK A SÜTIT!
        response.set_cookie(
            cookie_name,
            "accepted",
            max_age=365*24*60*60,
            path="/",
            secure=False,
            httponly=False,
            samesite="Lax"
        )

    return response

def decline_cookie_group(request, group_name):
    """
    Elutasítja az adott cookie csoportot, és eltárolja a sütiben.
    """
    cookie_group = CookieGroup.objects.filter(varname=group_name).first()
    if not cookie_group:
        return JsonResponse({"error": "Invalid cookie group"}, status=400)

    response_data = {
        "status": "declined"
    }

    # 🔹 Hozzuk létre a JSON választ külön
    response = JsonResponse(response_data)

    # 🔹 Kényszerítsük ki a sütibeállítást "declined" értékkel
    cookie_name = f"cookie_consent_{group_name}"
    response.set_cookie(
        cookie_name,
        "declined",
        max_age=365*24*60*60,
        path="/",
        secure=False,  # Ha HTTPS-en fut, állítsd True-ra!
        httponly=False,  # Ha True, akkor JS nem tudja olvasni
        samesite="Lax"
    )

    print(f"📩 Set-Cookie küldve: {cookie_name}=declined")  # 🔹 Debug log

    return response


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
    blogpost = get_object_or_404(BlogPost, slug=slug)
    contact = Contact.objects.first() 
    context = {'blogpost': blogpost, 'services': services, 'contact': contact, 'blogpost': blogpost}

    return render(request, 'blogpost.html', context)



