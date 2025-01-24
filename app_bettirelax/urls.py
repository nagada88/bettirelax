from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
# from .sitemaps import StaticSitemap, BlogSitemap 
# from .views import BlogPostDetailView

# sitemaps = {
#     'static':StaticSitemap, #add StaticSitemap to the dictionary
#     'blog':BlogSitemap #add StaticSitemap to the dictionary
# }

urlpatterns = [
    # path('blog/<slug:slug>/', BlogPostDetailView.as_view(), name='blog_detail'),    
    path('', views.introduction, name='introduction'),
    path('introduction/', views.introduction, name='introduction'),
    # path(r'services/', views.services, name='services'),
    # path(r'prices/', views.prices, name='prices'),
    # path(r'aboutme/', views.aboutme, name='aboutme'),
    # path('blog/', views.blog, name='blog'),
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # path(r'contact/', views.contact, name='revicontactew'),
    ]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)