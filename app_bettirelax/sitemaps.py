from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, BlogPost

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["introduction", "pricelist", "faq"]

    def location(self, item):
        return reverse(item)

class ServiceSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Service.objects.all()

class BlogSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return BlogPost.objects.all()