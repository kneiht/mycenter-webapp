from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

urlpatterns = [
    path('', include('app_accounts.urls')),
    path('', include('app_dashboard.urls')),
    path('', include('app_portal.urls')),
    path('admin/', admin.site.urls), 
    path('', include('pwa.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


