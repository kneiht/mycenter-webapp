
from . import views

from django.urls import path


urlpatterns = [
    path('portal/', views.portal_app, name='portal'),
    path('portal/profile/', views.portal_profile, name='portal_profile'),
    path('portal/profile/<int:school_id>/<int:student_id>/', views.portal_profile, name='portal_profile'),
    
    
    path('portal/calendar/<int:school_id>/<int:student_id>/', views.portal_calendar, name='portal_calendar'),
    path('portal/zalo/<int:school_id>/<int:student_id>/', views.portal_zalo, name='portal_zalo'),
    path('portal/portal_rules_benefits/', views.portal_rules_benefits, name='portal_rules_benefits'),
    path('portal/login/', views.portal_login, name='portal_login'),
    path('portal/logout/', views.portal_logout, name='portal_logout'),
]       