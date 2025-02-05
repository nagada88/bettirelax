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
    path('masszas-szigetszentmikloson/', views.introduction, name='introduction'),
    path('masszazs-szigetszentmiklos/<slug:slug>/', views.service, name='service'),
    path('blogpost/<slug:slug>/', views.blogpost, name='blogpost'),
    path('pricelist/', views.pricelist, name='pricelist'),
    path('bloglist/', views.bloglist, name='bloglist'),
    path('faq/', views.faq, name='faq'),
    path("cookie-status/", views.cookie_status, name="cookie_status"),
    path("cookie-accept/<str:group_name>/", views.accept_cookie_group, name="accept_cookie_group"),
    path("cookie-decline/<str:group_name>/", views.decline_cookie_group, name="decline_cookie_group"),
    path("status/", views.cookie_status, name="cookie_status"), 
    ]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)