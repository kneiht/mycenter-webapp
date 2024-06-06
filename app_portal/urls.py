
from . import views

from django.urls import path


urlpatterns = [
    path('portal/', views.portal_home, name='portal_home'),
    path('portal/login/', views.portal_login, name='portal_login'),
]       