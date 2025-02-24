from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from cookie_consent.util import get_cookie_value_from_request
from cookie_consent.models import CookieGroup
from django.shortcuts import redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from app_booking.models import BookingSettings
def contact_context(request):
    """
    Globális context processor, amely a kapcsolati adatokat elküldi az összes view-ba.
    """
    return { 'contact': Contact.objects.first()}

def cookie_banner_context(request):
    """
    Globális context processor, amely az összes cookie groupot elküldi a template-be.
    """
    return {"cookie_groups": CookieGroup.objects.all()}

def cookie_status(request):
    """
    Ellenőrzi a cookie-k állapotát, és visszaküldi JSON formátumban.
    """

    cookie_groups = CookieGroup.objects.all()
    
    cookie_status = {}
    for group in cookie_groups:
        cookie_name = f"cookie_consent_{group.varname}"
        cookie_value = request.COOKIES.get(cookie_name)  # 🔹 Olvassuk ki a sütit

        if cookie_value is None:
            is_accepted = None
        else:
            is_accepted = cookie_value == "accepted"

        cookie_status[group.varname] = {
            "accepted": is_accepted,
            "scripts": []
        }

        # 🔹 Ha az analytics süti ELFOGADOTT, akkor adjuk hozzá a GA4 scriptet
        if group.varname == "analytics" and is_accepted:
            cookie_status[group.varname]["scripts"].append(
                '<script async src="https://www.googletagmanager.com/gtag/js?id=G-YPZ37N9EBB"></script>'
                '<script>'
                '  window.dataLayer = window.dataLayer || [];'
                '  function gtag(){dataLayer.push(arguments);}'
                '  gtag("js", new Date());'
                '  gtag("config", "G-YPZ37N9EBB");'
                '</script>'
            )


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
    if group_name == "analytics":
        response_data["scripts"].append(
                '<script async src="https://www.googletagmanager.com/gtag/js?id=G-YPZ37N9EBB"></script>'
                '<script>'
                '  window.dataLayer = window.dataLayer || [];'
                '  function gtag(){dataLayer.push(arguments);}'
                '  gtag("js", new Date());'
                '  gtag("config", "G-YPZ37N9EBB");'
                '</script>'
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

    return response


def introduction(request):
    aboutme = AboutMe.objects.first() 
    services = Service.objects.all()
    booking_settings = BookingSettings.objects.first()
    title = "Masszázs Szigetszentmiklóson - Svédmasszázs, Aromaterápiás és Babamasszázs | Bettirelax"
    reviews = load_more_reviews(request)
    context = {'aboutme': aboutme, 'services': services, 'title': title, 'reviews': reviews, 'booking_settings': booking_settings}

    return render(request, 'introduction.html', context)

def review_upload(request):
    reviews = load_more_reviews(request)
    return render(request, 'review_partial.html',  {'reviews': reviews}) 

def load_more_reviews(request):
    page = request.GET.get("page")
    reviews = Review.objects.all()
    paginator = Paginator(reviews, 3)

    for review in reviews:
        review.remaining_stars = 5 - review.stars

    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    return reviews

def service(request, slug):
    service = get_object_or_404(Service, slug=slug)
    services = Service.objects.prefetch_related('prices').all() 
    context = {'services': services, 'service': service, 'title': service.service_name + "Szigetszentmiklóson"}

    return render(request, 'service.html', context)

def pricelist(request):
    services = Service.objects.prefetch_related('prices').all()  
    context = {'services': services, 'title': 'Masszázs Árak Szigetszentmiklóson – Frissítő és Relaxáló Masszázs'}
               
    return render(request, 'pricelist.html', context)

def faq(request):
    faqs = Faq.objects.all()
    aboutme = AboutMe.objects.first() 
    services = Service.objects.all()
    context = {'faqs': faqs, 'services': services, 'aboutme': aboutme, 'title': "Masszázs GYIK - Minden, Amit Tudni Érdemes a Kezelésekről"}

    return render(request, 'faq.html', context)

def bloglist(request):
    services = Service.objects.all()
    bloglist = BlogPost.objects.all()
    context = {'services': services, 'bloglist': bloglist, 'title': 'Blogposztok: Minden Ami Masszázs, Érdekességek, Esetek'}

    return render(request, 'bloglist.html', context)

def blogpost(request, slug):
    services = Service.objects.all()
    blogpost = get_object_or_404(BlogPost, slug=slug)
    title = blogpost.title
    context = {'blogpost': blogpost, 'services': services, 'blogpost': blogpost, 'title': title}

    return render(request, 'blogpost.html', context)

# def booking(request):
#     services = Service.objects.all()
#     context = {'services': services,'title': 'Időpontfoglalás Masszázs Szigetszentmiklós'}

#     return render(request, 'booking_temp.html', context)



