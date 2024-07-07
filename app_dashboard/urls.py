
from . import views, views_db
from .views import (
    StudentConvertViewSet, CMRViewSet, CRMNoteViewSet, SchoolViewSet, ClassViewSet, StudentViewSet, StudentNoteViewSet, TuitionPaymentViewSet, ClassRoomViewSet, TuitionPaymentOldViewSet, TuitionPaymentSpecialViewSet,
    FinancialTransactionViewSet, AttendanceViewSet, StudentAttendanceCalendarViewSet,home,wheel,calculate_student_balance, landing_page
)

from django.urls import re_path, path


urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('wheel', wheel, name='wheel'),
    path('calculate', calculate_student_balance, name='calculate_student_balance'),
    re_path(r'.*\.html', views.html_page, name='specific_page'),

    path('schools/', SchoolViewSet.as_view(), name='schools'),
    path('schools/<int:pk>/', SchoolViewSet.as_view(), name='school_detail'),

    path('schools/<int:school_id>/dashboard/', views.dashboard, name='dashboard'),

    path('schools/<int:school_id>/classes/', ClassViewSet.as_view(), name='classes'),
    path('schools/<int:school_id>/classes/<int:pk>/', ClassViewSet.as_view(), name='classroom'),
    path('schools/<int:school_id>/classes/<int:class_id>/<int:pk>/', ClassRoomViewSet.as_view(), name='classroom_student'),

    path('schools/<int:school_id>/students/', StudentViewSet.as_view(), name='students'),
    path('schools/<int:school_id>/students/<int:pk>/', StudentViewSet.as_view(), name='student_detail'),
    path('schools/<int:school_id>/students/<int:pk>/note/', StudentNoteViewSet.as_view(), name='student_detail_note'),
    path('schools/<int:school_id>/students/<int:pk>/convert/', StudentConvertViewSet.as_view(), name='crm_convert'),



    path('schools/<int:school_id>/crm/', CMRViewSet.as_view(), name='crm'),
    path('schools/<int:school_id>/crm/<int:pk>/', CMRViewSet.as_view(), name='crm_detail'),
    path('schools/<int:school_id>/crm/<int:pk>/note/', CRMNoteViewSet.as_view(), name='crm_detail_note'),
    path('schools/<int:school_id>/crm/<int:student_id>/attendance-calendar/', StudentAttendanceCalendarViewSet.as_view(), name='student_attendance_calendar'),


    path('schools/<int:school_id>/students/<int:student_id>/attendance-calendar/', StudentAttendanceCalendarViewSet.as_view(), name='student_attendance_calendar'),
    path('schools/<int:school_id>/students/<int:student_id>/pay-tuition/', TuitionPaymentViewSet.as_view(), name='pay_tuition'),
    path('schools/<int:school_id>/students/<int:student_id>/pay-tuition-old/', TuitionPaymentOldViewSet.as_view(), name='pay_tuition_old'),
    path('schools/<int:school_id>/students/<int:student_id>/pay-tuition-special/', TuitionPaymentSpecialViewSet.as_view(), name='pay_tuition_special'),

    path('schools/<int:school_id>/students/<int:student_id>/attendance-calendar/view/', views.student_attendance_calendar_view, name='student_attendance_calendar_view'),
    path('schools/<int:school_id>/students/<int:student_id>/view/', views.student_view, name='student_view'),
    


    path('schools/<int:school_id>/attendances/', AttendanceViewSet.as_view(), name='attendances'),
    path('schools/<int:school_id>/attendances/<int:pk>/', AttendanceViewSet.as_view(), name='attendance_detail'),


    re_path(r'^schools/(?P<school_id>\d+|[a-z]+)/financialtransactions/?$', FinancialTransactionViewSet.as_view(), name='financialtransactions'),
    re_path(r'^schools/(?P<school_id>\d+|[a-z]+)/financialtransactions/(?P<pk>\d+)/?$', FinancialTransactionViewSet.as_view(), name='financialtransaction_detail'),


    
    # path('classroom/<int:pk>/', views.classroom, name='classroom'),

    # DATABASE UPLOAD AND DOWNLOAD
    path('download_database_backup/', views_db.download_database_backup, name='download_database_backup'),
    path('database_handle/', views_db.database_handle, name='database_handle'),
]

# urlpatterns = [
#     re_path(r'^schools/?$', SchoolViewSet.as_view(), name='schools'),
#     re_path(r'^schools/(?P<pk>\d+)/?$', SchoolViewSet.as_view(), name='school_detail'),

#     re_path(r'^schools/(?P<school_id>\d+)/dashboard/?$', views.dashboard, name='dashboard'),

#     re_path(r'^schools/(?P<school_id>\d+)/classes/?$', ClassViewSet.as_view(), name='classes'),
#     re_path(r'^schools/(?P<school_id>\d+)/classes/(?P<pk>\d+)/?$', ClassViewSet.as_view(), name='classroom'),

#     re_path(r'^schools/(?P<school_id>\d+)/students/?$', StudentViewSet.as_view(), name='students'),
#     re_path(r'^schools/(?P<school_id>\d+)/students/(?P<pk>\d+)/?$', StudentViewSet.as_view(), name='student_detail'),

#     re_path(r'^schools/(?P<school_id>\d+)/attendances/?$', AttendanceViewSet.as_view(), name='attendances'),
#     re_path(r'^schools/(?P<school_id>\d+)/attendances/(?P<pk>\d+)/?$', AttendanceViewSet.as_view(), name='attendance_detail'),

#     re_path(r'^schools/(?P<school_id>\d+)/financialtransactions/?$', FinancialTransactionViewSet.as_view(), name='financialtransactions'),
#     re_path(r'^schools/(?P<school_id>\d+)/financialtransactions/(?P<pk>\d+)/?$', FinancialTransactionViewSet.as_view(), name='financialtransaction_detail'),

    
#     #re_path(r'^classroom/(?P<pk>\d+)/?$', views.classroom, name='classroom'),

#     # DATABASE UPLOAD AND DOWNLOAD
#     re_path(r'^download_database_backup/?$', views_db.download_database_backup, name='download_database_backup'),
#     re_path(r'^database_handle/?$', views_db.database_handle, name='database_handle'),

# ]
