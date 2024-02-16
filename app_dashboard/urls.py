from django.urls import re_path
from django.contrib.auth import views as auth_views
from . import views, views_db, api

from .views import SchoolViewSet, ClassViewSet, StudentViewSet



from django.urls import re_path
from . import views


urlpatterns = [
    re_path(r'^schools/?$', SchoolViewSet.as_view(), name='schools'),
    re_path(r'^schools/(?P<pk>\d+)/?$', SchoolViewSet.as_view(), name='schools_pk'),

    re_path(r'^schools/(?P<school_id>\d+)/dashboard/?$', views.dashboard, name='dashboard'),

    re_path(r'^schools/(?P<school_id>\d+)/classes/?$', ClassViewSet.as_view(), name='classes'),
    re_path(r'^schools/(?P<school_id>\d+)/classes/(?P<pk>\d+)/?$', ClassViewSet.as_view(), name='classroom'),

    re_path(r'^schools/(?P<school_id>\d+)/students/?$', StudentViewSet.as_view(), name='students'),
    re_path(r'^schools/(?P<school_id>\d+)/students/(?P<pk>\d+)/?$', StudentViewSet.as_view(), name='students_pk'),

    re_path(r'^schools/(?P<school_id>\d+)/attendances/?$', StudentViewSet.as_view(), name='attendances'),
    re_path(r'^schools/(?P<school_id>\d+)/attendances/(?P<pk>\d+)/?$', StudentViewSet.as_view(), name='attendances_pk'),


    
    #re_path(r'^classroom/(?P<pk>\d+)/?$', views.classroom, name='classroom'),

    # DATABASE UPLOAD AND DOWNLOAD
    re_path(r'^download_database_backup/?$', views_db.download_database_backup, name='download_database_backup'),
    re_path(r'^database_handle/?$', views_db.database_handle, name='database_handle'),

]





'''
    # CRUD APIs
    re_path(r'^dashboard/api/courses/?$', api.CourseListCreateView.as_view(), name='course_list_create'),
    re_path(r'^dashboard/api/courses/(?P<pk>\d+)/?$', api.CourseDetailView.as_view(), name='course_detail'),
    re_path(r'^dashboard/api/classschedules/?$', api.ClassScheduleListCreateView.as_view(), name='classschedule_list_create'),
    re_path(r'^dashboard/api/classschedules/(?P<pk>\d+)/?$', api.ClassScheduleDetailView.as_view(), name='classschedule_detail'),
    re_path(r'^dashboard/api/classes/?$', api.ClassListCreateView.as_view(), name='class_list_create'),
    re_path(r'^dashboard/api/classes/(?P<pk>\d+)/?$', api.ClassDetailView.as_view(), name='class_detail'),
    re_path(r'^dashboard/api/students/?$', api.StudentListCreateView.as_view(), name='student_list_create'),
    re_path(r'^dashboard/api/students/(?P<pk>\d+)/?$', api.StudentDetailView.as_view(), name='student_detail'),
    re_path(r'^dashboard/api/tuitionplans/?$', api.TuitionPlanListCreateView.as_view(), name='tuitionplan_list_create'),
    re_path(r'^dashboard/api/tuitionplans/(?P<pk>\d+)/?$', api.TuitionPlanDetailView.as_view(), name='tuitionplan_detail'),
    re_path(r'^dashboard/api/discounts/?$', api.DiscountListCreateView.as_view(), name='discount_list_create'),
    re_path(r'^dashboard/api/discounts/(?P<pk>\d+)/?$', api.DiscountDetailView.as_view(), name='discount_detail'),
    re_path(r'^dashboard/api/attendances/?$', api.AttendanceListCreateView.as_view(), name='attendance_list_create'),
    re_path(r'^dashboard/api/attendances/(?P<pk>\d+)/?$', api.AttendanceDetailView.as_view(), name='attendance_detail'),
    re_path(r'^dashboard/api/financialtransactions/?$', api.FinancialTransactionListCreateView.as_view(), name='financialtransaction_list_create'),
    re_path(r'^dashboard/api/financialtransactions/(?P<pk>\d+)/?$', api.FinancialTransactionDetailView.as_view(), name='financialtransaction_detail'),
    re_path(r'^dashboard/api/transactionimages/?$', api.FinancialTransactionListCreateView.as_view(), name='transactionimage_list_create'),
    re_path(r'^dashboard/api/transactionimages/(?P<pk>\d+)/?$', api.FinancialTransactionDetailView.as_view(), name='transactionimage_detail'),
    re_path(r'^dashboard/api/fetch_records/?$', views.fetch_records, name='fetch_records'),
    re_path(r'^dashboard/api/fetch_one_record/?$', views.fetch_one_record, name='fetch_one_record'),





    # FORM GENERATOR
    re_path(r'^manage/form_generator/?$', views.form_generator, name='form_generator'),

    # CLASS MANAGEMENT RELATED
    re_path(r'^manage/classes/?$', views.manage_classes, name='manage_classes'),
    re_path(r'^manage/classes/(?P<pk>\d+)/?$', views.manage_one_class, name='manage_one_class'),
    re_path(r'^manage/api/class_attendance/(?P<pk>\d+)/?$', views.class_attendance, name='class_attendance'),
    re_path(r'^manage/api/add_money_to_students/?$', views.add_money_to_students, name='add_money_to_students'),

    # STUDENT MANAGEMENT RELATED
    re_path(r'^manage/students/(?P<pk>\d+)/attendance-calendar/?$', views.student_attendance_calendar, name='student_attendance_calendar'),


    # OTHER MODELS
    re_path(r'^manage/(?P<model_name_plural>\w+)/?$', views.manage_other_models, name='manage_other_models'),
'''