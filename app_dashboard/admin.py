
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import School, SchoolUser, UserProfile, Values, Student, Class, StudentClass, Attendance, FinancialTransaction
from django.utils.safestring import mark_safe
from django import forms

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'moved_to_trash')
    list_filter = ('moved_to_trash',)
    search_fields = ('name', 'description')

class SchoolUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'gender', 'date_of_birth', 'phone', 'bio', 'image', 'settings', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone', 'bio')

class ValuesAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'key', 'value')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'date_of_birth', 'parents', 'phones', 'status', 'reward_points', 'balance', 'image', 'image_portrait', 'note', 'last_note', 'created_at')
    list_filter = ('created_at', 'status')
    search_fields = ('name', 'parents', 'phones')

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'price_per_hour', 'note', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)

class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_name', 'is_payment_required')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'check_class', 'check_date', 'status', 'learning_hours', 'price_per_hour', 'is_payment_required', 'note', 'created_at')
    list_filter = ('check_date', 'status')
    search_fields = ('student__name', 'check_class__name', 'check_date')

class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('get_transaction_type_display', 'income_or_expense', 'amount', 'student', 'bonus', 'student_balance_increase', 'legacy_discount', 'legacy_tuition_plan', 'note', 'created_at')
    list_filter = ('created_at', 'income_or_expense', 'transaction_type')
    search_fields = ('student__name', 'receiver')

admin.site.register(School, SchoolAdmin)
admin.site.register(SchoolUser, SchoolUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Values, ValuesAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(StudentClass, StudentClassAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(FinancialTransaction, FinancialTransactionAdmin)
