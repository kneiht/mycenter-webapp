
from . import views

from django.urls import path


urlpatterns = [
    path('portal/', views.portal_app, name='portal'),
    path('portal/profile/', views.portal_profile, name='portal_profile'),
    path('portal/calendar/', views.portal_calendar, name='portal_calendar'),
    path('portal/zal]o/', views.portal_zalo, name='portal_zalo'),
    path('portal/login/', views.portal_login, name='portal_login'),
]       