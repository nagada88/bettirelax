from django.shortcuts import render

# Create your views here.

def introduction(request):
    # pictures = Photos.objects.filter(category__name="kutyafotózás")
    # studiopictures = Photos.objects.filter(category__name="studio")
    # reviews = load_more_reviews(request)
    return render(request, 'introduction.html')
