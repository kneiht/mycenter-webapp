# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user

# Python Standard Library Imports
import json

import os
from django.conf import settings

from datetime import datetime, timedelta
from collections import defaultdict 
import time
from calendar import monthrange

# Django and Other Third-Party Imports
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect

from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Count, Sum  # 'Sum' is imported here

# Import forms
from .forms import (
    SchoolForm, StudentForm, ClassForm, AttendanceForm, FinancialTransactionForm, 
    TuitionPaymentForm, TuitionPaymentOldForm, TuitionPaymentSpecialForm, StudentNoteForm, StudentConvertForm
)
# Import models
from django.contrib.auth.models import User
from .models import (
    School, Student, SchoolUser, Class, StudentClass, Attendance, FinancialTransaction
)
from django.db.models import F, FloatField


from .html_render import html_render

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


# GENERAL PAGES ==============================================================
def landing_page(request):
    if settings.DOMAIN == 'mycenter':
        return redirect('schools')
    else:
        return render(request, 'pages/landing_page.html')

import os
from django.shortcuts import render

def html_page(request):
    # This view is for all pages ended with html 
    # check the file in the url, get the file name and return it
    file_name = request.path.split('/')[-1]  # Get the file name from the URL
    file_name = file_name.replace('-', '_')
    file_path = os.path.join('pages/', file_name)  # Replace 'path_to_your_html_files' with the actual path to your HTML files
    return render(request, file_path)


@login_required
def dashboard(request, school_id):
    #school = School.objects.filter(pk=school_id).first()
    #context = {'page': 'dashboard', 'title': 'Dashboard', 'school': school}
    #return render(request, 'pages/single_page.html', context)
    return redirect('classes', school_id=school_id)


@login_required
def calculate_student_balance(request):
    students = Student.objects.all()
    for student in students:
        # Summarize all student_balance_increase from FinancialTransaction
        total_increase = FinancialTransaction.objects.filter(student=student).aggregate(Sum('student_balance_increase'))['student_balance_increase__sum'] or 0
        
        # Calculate total attendance cost
        total_attendance_cost = Attendance.objects.filter(student=student, is_payment_required=True).annotate(
            total_cost=Sum(F('learning_hours') * F('price_per_hour'), output_field=FloatField())
        ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0
        
        # Calculate final balance
        student.balance = total_increase - total_attendance_cost
        student.save()
    return redirect('schools')


@login_required
def home(request):
    return redirect('schools')



@login_required
def wheel(request):
    rendered_page = render(request, 'pages/wheel.html')
    return rendered_page



# DATABASE MANAGEMENT VIEWS
#------------------------------
class BaseViewSet(LoginRequiredMixin, View):
    model_class = None
    form_class = None
    title =  None
    page = None
    modal = None

    def get(self, request, school_id=None, pk=None):
        get_query = request.GET.get('get')
        if get_query=='form':
            return self.create_form(request, school_id=school_id, pk=pk)
        else:
            return self.create_display(request, school_id=school_id)

    def delete(self, request, school_id=None, pk=None):
        # Get the record and put it in a list for later deletion
        record = get_object_or_404(self.model_class, pk=pk)
        # Delete the record
        if 'confirm' in request.POST:
            record.delete()
            # Return a success message
            html_message = html_render('message', request, message='Delete successfully')
        else:
            # return confirmation message
            html_message = html_render('message', request, message_type="confirm_delete", message='Do yo really want to delete this record?')
        
        return HttpResponse(html_message)


    def post(self, request, school_id=None, pk=None):
        school = School.objects.filter(pk=school_id).first()
        if pk:
            instance = get_object_or_404(self.model_class, id=pk)

        # if there is delete = true in data form
        if 'delete' in request.POST and request.POST.get('delete')=='true':
            return self.delete(request, school_id=school_id, pk=pk)
            
        result, instance, form = self.process_form(request, instance if pk else None)
        if result=='success':
            # add payment in students page
            if self.page=='students' and type(instance)==FinancialTransaction:
                instance = instance.student

            instance.style = 'just-updated'
            html_display_cards = html_render('display_cards', request, select=self.page, records=[instance], school=school)
            html_message = html_render('message', request, message='create successfully')
            return HttpResponse(html_display_cards + html_message)
        else:
            record_id=instance.pk if instance else None
            html_modal = html_render('form', request, form=form, modal=self.modal, record_id=record_id, school=school)
            return HttpResponse(html_modal)



    def check_school_user(self, request, school_id):
        school = School.objects.filter(pk=school_id).first()
        school_user = SchoolUser.objects.filter(school=school, user=request.user).first()
        if school_user:
            return True
        else:
            return False

    def create_display(self, request, **kwargs):
        school_id = kwargs.pop('school_id', None)

        if self.model_class==School:
            user = request.user
            records = self.model_class.objects.filter(users=user)
        elif self.model_class in [Student, Class, FinancialTransaction, Attendance]:
            if self.check_school_user(request, school_id):
                records = self.model_class.objects.filter(school_id=school_id)
            else:
                return HttpResponseForbidden("Access restricted to users of the school.")

        # filter for Students and CRM
        if self.page=='students':
            # filter status "enrolled, on_hold, discontinued"
            records = records.filter(status__in=['enrolled', 'on_hold', 'discontinued'])
        elif self.page=='CRM':
            records = records.filter(status__in=['potential_customer', 'not_contacted_customer', 'not_potential_customer', 'just_added'])


        # Determine the fields to be used as filter options based on the selected page
        if self.page == 'schools':
            fields = ['all', 'name', 'description']
        elif self.page == 'students' or self.page == 'CRM':
            fields = ['all', 'name','status', 'gender', 'parents', 'phones']
        elif self.page == 'classes':
            fields = ['all', 'name']
        elif self.page == 'financial_transactions':
            fields = ['all', 'amount']
        else:
            fields = ['all']

        # Get all query parameters except 'sort' as they are assumed to be field filters
        query_params = {k: v for k, v in request.GET.lists() if k != 'sort'}
        # Construct Q objects for filtering
        combined_query = Q()
        if 'all' in query_params:
            specified_fields = fields[1:]  # Exclude 'all' to get the specified fields
            all_fields_query = Q()
            for value in query_params['all']:
                for specified_field in specified_fields:
                    if specified_field in [field.name for field in self.model_class._meta.get_fields()]:
                        all_fields_query |= Q(**{f"{specified_field}__icontains": value})
            combined_query &= all_fields_query
        else:
            for field, values in query_params.items():
                if field in fields:
                    try:
                        self.model_class._meta.get_field(field)
                        field_query = Q()
                        for value in values:
                            field_query |= Q(**{f"{field}__icontains": value})
                        combined_query &= field_query
                    except FieldDoesNotExist:
                        print(f"Ignoring invalid field: {field}")

        # Filter records based on the query
        records = records.filter(combined_query)

        # Filter records based on the query
        records = records.filter(combined_query)

        # Sort the results if the sort field exists in the model
        # Get the and sort option from the request
        sort_option = request.GET.get('sort', 'default')
        if sort_option and hasattr(self.model_class, sort_option):
            if sort_option == 'last_saved':
                # filter enrolled
                records = records.order_by('-last_saved')
            else:
                records = records.order_by(sort_option)
        else:
            if sort_option == 'balance_up_active':
                # filter enrolled
                records = records.filter(status='enrolled')
                records = records.order_by('balance')
            elif sort_option == 'balance_up':
                records = records.order_by('balance')

            else:
                records = records.order_by('-pk')

        context = {
            'select': self.page, 
            'title': self.title, 
            'records': records,
            'fields':  fields,
            'school': School.objects.filter(pk=school_id).first() if school_id else None
        }
        return render(request, 'pages/single_page.html', context)

    def create_form(self, request, **kwargs):
        school_id = kwargs.pop('school_id', None)
        pk = kwargs.pop('pk', None)

        # Get the instance if pk is provided, use None otherwise
        record = self.model_class.objects.filter(pk=pk).first() if pk!='new' else None
        
        # Pass school_id to the form of classes
        if self.form_class==ClassForm:
            form = self.form_class(instance=record, school_id=school_id) if record else self.form_class(school_id=school_id)
            record_id = record.pk if record else None
        
        elif self.form_class==StudentForm:
            form = self.form_class(instance=record, school_id=school_id) if record else self.form_class(school_id=school_id)
            record_id = record.pk if record else None


        elif self.form_class in [TuitionPaymentForm, TuitionPaymentOldForm, TuitionPaymentSpecialForm]: 
            student_id = kwargs.pop('student_id', None)
            student = Student.objects.filter(pk=student_id).first()
            initial_data = {
                'income_or_expense': 'income',
                'transaction_type': 'income_tuition_fee',
                'student': student,
                'receiver': School.objects.filter(pk=school_id).first(),
            }
            form = self.form_class(initial = initial_data, school_id=school_id, student_id=student_id)
            record_id = student.pk




        elif self.form_class==AttendanceForm:
            student_id = request.GET.get('student_id')
            check_date = request.GET.get('check_date')
            # convert check_date to date object
            if check_date:
                check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
            else:
                check_date = datetime.now().date()
            student = Student.objects.filter(pk=student_id).first()
            initial_data = {
                'student': student,
                'check_date':check_date,
            }
            form = self.form_class(instance=record, school_id=school_id) if record else self.form_class(initial = initial_data, school_id=school_id)
            record_id = record.pk if record else None

        else:
            form = self.form_class(instance=record) if record else self.form_class()
            record_id = record.pk if record else None


        html_modal = html_render('form', request, form=form, 
                                 modal=self.modal, record_id=record_id, 
                                 record = record if record else None,
                                 school_id=school_id)
        return  HttpResponse(html_modal)

    def process_form(self, request, instance=None):
        form = self.form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            if self.model_class == School:
                instance_form = form.save(commit=False)
                instance_form.save()
                if not instance:
                    school_user = SchoolUser(school=instance_form, user=request.user)
                    school_user.save()
            else:
                school = School.objects.filter(pk=request.POST.get('school_id')).first()
                school_user = SchoolUser.objects.filter(school=school, user=request.user).first()
                if school_user:
                    instance_form = form.save(commit=False)
                    if not instance:
                        instance_form.school = school
                    instance_form.save()

                    if  self.form_class == ClassForm:
                        form.save_m2m()      

                        # Data from the client
                        student_ids = request.POST.getlist('students')
                        payment_required_ids = request.POST.getlist('payment_required')

                        # Existing student-class relationships
                        existing_student_classes = StudentClass.objects.filter(_class=instance_form)

                        # Update existing relationships
                        for student_class in existing_student_classes:
                            if str(student_class.student.id) in student_ids:
                                student_class.is_payment_required = str(student_class.student.id) in payment_required_ids
                                student_class.save()
                                student_ids.remove(str(student_class.student.id))
                            else:
                                # Remove the student from the class if they're no longer included
                                student_class.delete()

                        # Add new students to the class
                        for student_id in student_ids:
                            student = Student.objects.get(id=student_id)
                            StudentClass.objects.create(
                                student=student,
                                _class=instance_form,
                                is_payment_required=student_id in payment_required_ids,
                            )
                        return 'success', instance_form, form

                    elif self.form_class == StudentForm:
                        form.save_m2m()
                        # Data from the client
                        class_ids = request.POST.getlist('classes')
                        payment_required_ids = request.POST.getlist('payment_required')

                        # Existing student-class relationships
                        existing_student_classes = StudentClass.objects.filter(student=instance_form)

                        # Update existing relationships
                        for student_class in existing_student_classes:
                            if str(student_class._class.id) in class_ids:
                                student_class.is_payment_required = str(student_class._class.id) in payment_required_ids
                                student_class.save()
                                class_ids.remove(str(student_class._class.id))
                            else:
                                # Remove the student from the class if they're no longer included
                                student_class.delete()

                        # Add new students to the class
                        for class_id in class_ids:
                            _class = Class.objects.get(id=class_id)
                            StudentClass.objects.create(
                                _class=_class,
                                student=instance_form,
                                is_payment_required=class_id in payment_required_ids,
                            )
                        return 'success', instance_form, form

            return 'success', instance_form, form
        else:
            return 'failed', instance, form





class SchoolViewSet(BaseViewSet):
    model_class = School
    form_class = SchoolForm
    title =  'Manage Schools'
    page = 'schools'
    modal = 'modal_school'
    def share_school(request, school_id):
        if request.method == 'POST':
            email = request.POST.get('email')
            try:
                user_to_share_with = User.objects.get(email=email)
                school = School.objects.get(id=school_id)
                # Assuming you have a method to share school with user
                school.share_with_user(user_to_share_with)
                return JsonResponse({'status': 'success', 'message': 'School shared successfully.'})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found.'})
            except School.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'School not found.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


class StudentViewSet(BaseViewSet):
    model_class = Student
    form_class = StudentForm
    title =  'Manage Students'
    modal = 'modal_student'
    page = 'students'

    def post(self, request, school_id=None, pk=None):
        return super().post(request, school_id, pk)


class StudentNoteViewSet(BaseViewSet):
    model_class = Student
    form_class = StudentNoteForm
    modal = 'modal_note'
    page = 'students'

    def post(self, request, school_id=None, pk=None):
        return super().post(request, school_id, pk)

class CMRViewSet(BaseViewSet):
    model_class = Student
    form_class = StudentForm
    title =  'Customer Relationship Management'
    modal = 'modal_student'
    page = 'CRM'

    def post(self, request, school_id=None, pk=None):
        return super().post(request, school_id, pk)

class CRMNoteViewSet(BaseViewSet):
    model_class = Student
    form_class = StudentNoteForm
    modal = 'modal_note'
    page = 'CRM'

    def post(self, request, school_id=None, pk=None):
        return super().post(request, school_id, pk)

class StudentConvertViewSet(BaseViewSet):
    model_class = Student
    form_class = StudentConvertForm
    modal = 'modal_convert_student'
    page = 'CRM'

    def post(self, request, school_id=None, pk=None):
        return super().post(request, school_id, pk)









def get_images(path):
    root_static_url = settings.STATIC_URL
    static_image_url = root_static_url + path
    meme_folder_path = os.path.join(settings.STATIC_ROOT, path)
    images_list = []
    for root, dirs, files in os.walk(meme_folder_path):

        images_list.extend(
            static_image_url + '/' + file
            for file in files
            if file.lower().endswith(('.png', '.jpg', '.jpeg'))
        )
    return images_list
class ClassViewSet(BaseViewSet):
    model_class = Class
    form_class = ClassForm
    title = 'Manage Classes'
    page = 'classes'
    modal = 'modal_class'

    success_images_list = get_images('images/memes/success')
    fail_images_list = get_images('images/memes/fail')

    def get(self, request, school_id=None, pk=None):
        get_query = request.GET.get('get')
        if get_query=='attendance':
            return self.get_attendance_by_class(request, school_id, pk)
        else:
            if get_query or not pk:
                return super().get(request, school_id, pk)
            else:
                return self.create_display_classroom(request, school_id, pk)

    def post(self, request, school_id=None, pk=None):
        post_query = request.GET.get('post')
        if post_query=='attendance':
            return self.update_class_attendance(request, school_id, pk)
        
        elif post_query=='reward':
            return  self.update_reward_points(request, school_id, pk)
        
        else:
            return super().post(request, school_id, pk)


    def create_display_classroom(self, request, school_id, pk):
        class_instance = get_object_or_404(Class, pk=pk)
        check_date = request.GET.get('check_date')
        if not check_date:
            check_date = datetime.now().date()
        students_in_class = Student.objects.filter(studentclass___class=class_instance)

        # style disable absent students
        for student in students_in_class:
            if not student.check_attendance(class_instance, check_date):
                student.style = 'grayouted'

        context = {
            'class_instance': class_instance,
            'records': students_in_class,
            'select': 'classroom',
            'title': f'{class_instance.name}',
            'school': School.objects.filter(pk=school_id).first(),
            'success_images_list': self.success_images_list,
            'fail_images_list': self.fail_images_list,
        }
        return render(request, 'pages/single_page.html', context)


    def get_attendance_by_class(self, request, school_id, pk):
        # Get class_id and checkDate from request parameters
        class_id = pk
        check_date_str = request.GET.get('check_date')  # 'YYYY-MM-DD'
        
        # Ensure class_id is provided
        if not class_id:
            html_message = render(request, 'message.html', {'message': 'Class ID is required'})
            return html_message

        # Attempt to fetch the class, return 404 if not found
        check_class = get_object_or_404(Class, id=class_id)
        # Parse checkDate string to date object if provided
        if check_date_str:
            try:
                # Try parsing the datetime string with the format '%Y-%m-%d'
                check_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # If parsing with '%Y-%m-%d' fails, try parsing with '%Y-%m-%dT%H:%M'
                    check_date = datetime.strptime(check_date_str, '%Y-%m-%dT%H:%M').date()
                except ValueError:
                    # Handle invalid date formats here
                    check_date = timezone.now().date()  

            # Filter Attendance records for the class on the specific date
            attendance_records = Attendance.objects.filter(
                check_class=check_class,
                check_date__date=check_date  # Assumes check_date is a DateTimeField
            ).select_related('student')

        # Serialize the attendance records
        attendance_data = [{
            'id': str(record.student_id),
            'student_name': str(record.student),  # Adjust according to your model
            'status': record.status,
            'check_date': record.check_date.strftime('%Y-%m-%d'),
            'is_payment_required': record.is_payment_required,
            'note': record.note,
        } for record in attendance_records]
        return JsonResponse({'status': 'success', 'attendance_data': attendance_data})


    def update_class_attendance(self, request, school_id, pk):
        # Parsing the JSON data
        class_id = pk
        data = request.POST
        print(data)
        check_date_str = data.get('check_date')  # Assuming 'checkDate' is sent in the format 'YYYY-MM-DD HH:MM'
        learning_hours = data.get('learning_hours')
        notes = data.get('notes')
        # Convert notes to dict
        if notes:
            notes = json.loads(notes)
        # Assuming 'school_id' can be directly used to find a class, adjust as needed
        check_class = get_object_or_404(Class, id=class_id)
        if not check_class:
            html_message = html_render('message', request, message='update attendance failed')
            return HttpResponse(html_message)

        # Function to process students by status
        def process_students(status, student_ids_str):
            if student_ids_str:
                student_ids = student_ids_str.split('-')
                for student_id in student_ids:
                    student = Student.objects.filter(id=student_id).first()
                    if student:
                        # Parse the check_date_str to a datetime object
                        try:
                            # If parsing with '%Y-%m-%d' fails, try parsing with '%Y-%m-%dT%H:%M'
                            check_datetime = datetime.strptime(check_date_str, '%Y-%m-%d')
                        except ValueError:
                            # Handle invalid date formats here
                            check_datetime = timezone.now()
                                
                        # Filter Attendance objects based on student and check_date
                        attendance = Attendance.objects.filter(
                            school_id=school_id,
                            student=student,
                            check_class=check_class,
                            check_date__date=check_datetime.date()
                        ).first()

                        # If an attendance record exists for the same date, update it
                        if attendance:
                            attendance.status = status
                            attendance.check_date = check_datetime  # Update check_datetime if needed
                            attendance.learning_hours = learning_hours
                            attendance.note = notes[str(student.pk)] if str(student.pk) in notes.keys() else ''
                            attendance.save()
                        else:
                            # Create a new Attendance record if none exists for the same date
                            attendance = Attendance.objects.create(
                                school_id=school_id,
                                student=student,
                                check_class=check_class,
                                check_date=check_datetime,  # Use the parsed check_datetime here
                                learning_hours = learning_hours,
                                status=status,
                                note = notes[str(student.pk)] if str(student.pk) in notes.keys() else ''
                            )

        # Process each status
        process_students('present', data.get('present', ''))
        process_students('absent', data.get('absent', ''))
        process_students('late', data.get('late', ''))
        process_students('left_early', data.get('left_early', ''))
        process_students('not_checked', data.get('not_checked', ''))



        html_message = html_render('message', request, message='update attendance successfully')
        return HttpResponse(html_message)


    def update_reward_points(self, request, school_id=None, pk=None):
        # Get the parameters from the URL
        reward_points = int(request.GET.get('reward_points'))
        student_ids = request.GET.get('students')
        # Split student_ids by "-" to get a list of individual student IDs
        student_id_list = student_ids.split('-')

        # Find the school (assuming you have a School model)
        school = get_object_or_404(School, pk=int(school_id))
        # Update reward points for selected students
        html = ''
        for student_id in student_id_list:
            try:
                student = Student.objects.filter(pk=int(student_id), school=school).first()
                student.reward_points += int(reward_points)
                student.save()
            except Exception as e:
                print(e)
        students = Student.objects.filter(pk__in=student_id_list, school=school)

        # add style for the card
        check_date = request.GET.get('check_date')
        class_id = pk
        class_instance = get_object_or_404(Class, pk=class_id)
        for student in students:
            if not student.check_attendance(class_instance, check_date):
                student.style = 'reward shake grayouted'
            else:
                student.style = 'reward shake'

        if int(reward_points) >= 0:
            message_type = 'reward-up'
            message_title = 'Update Reward Points'
            message = f'CHÚC MỪNG CÁC EM ĐÃ CÓ THÊM {abs(reward_points)} ĐIỂM THƯỞNG'
        else:
            message_type = 'reward-down'
            message_title = 'Update Reward Points'
            message = f'XIN CHIA BUỒN CÁC EM ĐÃ BỊ TRỪ {abs(reward_points)} ĐIỂM THƯỞNG'

        html += html_render('display_cards', request, select='classroom', records=students, school=school)
        html += html_render('message', request,message_title=message_title,message=message, message_type=message_type)
        return HttpResponse(html)





class ClassRoomViewSet(BaseViewSet):
    model_class = Student
    form_class = StudentForm
    title =  'Manage Student in Classroom'
    modal = 'modal_student'
    page = 'classroom'

    def get(self, request, school_id=None, class_id=None, pk=None):
        get_query = request.GET.get('get')
        if get_query=='form':
            return self.create_form(request, school_id=school_id, pk=pk)
        
    def post(self, request, school_id=None, class_id=None, pk=None):
        return super().post(request, school_id, pk)





class AttendanceViewSet(BaseViewSet):
    model_class = Attendance
    form_class = AttendanceForm
    title =  'Manage Attendance'
    modal = 'modal_attendance'
    page = 'attendance'




def student_attendance_calendar_view(request, school_id, student_id):
    request.mode = "view"
    return StudentAttendanceCalendarViewSet.student_attendance_calendar(request, school_id, student_id)
def student_view(request, school_id, student_id):
    return redirect('student_attendance_calendar_view', school_id=school_id, student_id=student_id) 
    

class StudentAttendanceCalendarViewSet(BaseViewSet):
    model_class = Attendance
    form_class = AttendanceForm
    title =  'Manage Attendance'
    modal = 'modal_attendance'
    page = 'attendance'

    def get(self, request, school_id=None, student_id=None):
        get_query = request.GET.get('get')
        return StudentAttendanceCalendarViewSet.student_attendance_calendar(request, school_id, student_id)


    @staticmethod
    def student_attendance_calendar(request, school_id, student_id):
        student = get_object_or_404(Student, pk=student_id)
        payment_id = request.GET.get('payment_id')
        payments = FinancialTransaction.objects.filter(student=student).order_by('created_at')
        all_attendances = Attendance.objects.filter(student=student).order_by('check_date')


        # remove attendances at the beginning of the list with status = 'not_checked' to make sure they are not shown
        # the list starts from the earliest attendance date with status != 'not_checked'
        for attendance in all_attendances:
            if attendance.status == 'not_checked':
                # Remove this attendannce from the query
                all_attendances = all_attendances.exclude(pk=attendance.pk)
            else:
                break

        if len(all_attendances)==0: #
            context = {
                'select': 'attendance',
                'page': 'attendance',
                'title': 'Attendance - ' + student.name,
                'school': School.objects.filter(pk=school_id).first(),
                'student': student,
            }
            return render(request, 'pages/single_page.html', context)



        if not payment_id or payment_id=="all":
            # Assume we fetch the earliest and latest attendance dates for the student to define the range
            # For demonstration, replace these with actual queries if available
            earliest_attendance_date = all_attendances.earliest('check_date').check_date
            latest_attendance_date = all_attendances.latest('check_date').check_date


        elif payment_id and (payment_id !="unpaid"):
            selected_payment = get_object_or_404(FinancialTransaction, pk=payment_id)
            # Calculate the balance before the selected payment
            balance_before_payment = 0
            for payment in payments:
                if payment.created_at < selected_payment.created_at:
                    balance_before_payment += payment.student_balance_increase
                    if payment == selected_payment:
                        break
            # Calculate the balance up to and including the selected payment
            balance_up_to_payment = balance_before_payment + selected_payment.student_balance_increase

            # Filter attendances based on the balance
            cumulative_balance = 0
            filtered_attendance_ids = []

            for attendance in all_attendances:
                if attendance.is_payment_required:
                    cumulative_balance += attendance.price_per_hour * attendance.learning_hours

                if (cumulative_balance > balance_before_payment) and (cumulative_balance <= balance_up_to_payment):
                    filtered_attendance_ids.append(attendance.id)

                elif cumulative_balance > balance_up_to_payment:
                    break
                

            attendances = Attendance.objects.filter(id__in=filtered_attendance_ids)
            earliest_attendance_date = attendances.earliest('check_date').check_date
            latest_attendance_date = attendances.filter(student=student).latest('check_date').check_date

        elif payment_id=="unpaid":
            balance = 0
            for payment in payments:
                balance += payment.student_balance_increase

            # Filter attendances based on the balance
            cumulative_balance = 0
            filtered_attendance_ids = []

            for attendance in all_attendances:
                if attendance.is_payment_required:
                    cumulative_balance += attendance.price_per_hour * attendance.learning_hours

                if cumulative_balance > balance:
                    filtered_attendance_ids.append(attendance.id)
            
            attendances = Attendance.objects.filter(id__in=filtered_attendance_ids)
            earliest_attendance_date = attendances.earliest('check_date').check_date
            latest_attendance_date = attendances.filter(student=student).latest('check_date').check_date



        # Adjust start_day and end_day to cover all attendance records
        start_day = earliest_attendance_date
        end_day = latest_attendance_date
        print(start_day, end_day)

        # Fetch attendances within the expanded date range
        attendances = Attendance.objects.filter(
            student=student,
            check_date__range=(start_day, end_day + timedelta(days=1))  # Add 1 day to include the last day
        ).order_by('check_date')



        # Organize attendances by date
        attendances_by_date = defaultdict(list)
        for attendance in attendances:
            attendances_by_date[attendance.check_date.date()].append(attendance)



        # Initialize data structure for months
        months = defaultdict(lambda: {'days': []})
        current_day = start_day
        while current_day <= end_day:

            day_data = {
                'date': current_day,
                'attendances': attendances_by_date.get(current_day.date(), []),
                'display': True,
            }
            months[current_day.strftime("%Y-%m")]['days'].append(day_data)
            current_day += timedelta(days=1)

        # iterate each month, then add leading empty days to make sure the first element in the list is monday
        for month, data in months.items():
            while data['days'][0]['date'].weekday() != 0:
                data['days'].insert(0, {'date': data['days'][0]['date'] - timedelta(days=1), 'attendances': [], 'display': False})

        # iterate each month, then add trailing empty days to make sure the last element in the list is sunday
        for month, data in months.items():
            while data['days'][-1]['date'].weekday() != 6:
                data['days'].append({'date': data['days'][-1]['date'] + timedelta(days=1), 'attendances': [], 'display': False})


        # Convert months to a list if you want a sorted result
        months_list = [{'month': month, 'days': data['days']} for month, data in sorted(months.items())]

        context = {
            'page': 'attendance',
            'select': 'attendance',
            'title': 'Attendance - ' + student.name,
            'school': School.objects.filter(pk=school_id).first(),
            'student': student,
            'months': months_list,
            'today': datetime.today(),
            'payments': payments,
            'selected_payment_id': payment_id,
            'view_only_url': request.build_absolute_uri(f'/schools/{school_id}/students/{student_id}/view/')
        }

        return render(request, 'pages/single_page.html', context)




class FinancialTransactionViewSet(BaseViewSet):
    model_class = FinancialTransaction
    form_class = FinancialTransactionForm
    title =  'Manage Financial Transactions'
    modal = 'modal_financial_transaction'
    page = 'financial_transactions'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class TuitionPaymentViewSet(BaseViewSet):
    model_class = FinancialTransaction
    form_class = TuitionPaymentForm
    title =  'Manage Tuition Payments'
    modal = 'modal_pay_tuition'
    page = 'students'

    def get(self, request, school_id=None, student_id=None, pk=None):
        get_query = request.GET.get('get')
        if get_query=='form':
            return self.create_form(request, school_id=school_id, student_id=student_id, pk=pk)
    def post(self, request, school_id=None, student_id=None, pk=None):
        return super().post(request, school_id, pk)

class TuitionPaymentOldViewSet(BaseViewSet):
    model_class = FinancialTransaction
    form_class = TuitionPaymentOldForm
    title =  'Manage Tuition Payments'
    modal = 'modal_pay_tuition_old'
    page = 'students'

    def get(self, request, school_id=None, student_id=None, pk=None):
        get_query = request.GET.get('get')
        if get_query=='form':
            return self.create_form(request, school_id=school_id, student_id=student_id, pk=pk)
    def post(self, request, school_id=None, student_id=None, pk=None):
        return super().post(request, school_id, pk)



class TuitionPaymentSpecialViewSet(BaseViewSet):
    model_class = FinancialTransaction
    form_class = TuitionPaymentSpecialForm
    title =  'Manage Tuition Payments'
    modal = 'modal_pay_tuition_special'
    page = 'students'

    def get(self, request, school_id=None, student_id=None, pk=None):
        get_query = request.GET.get('get')
        if get_query=='form':
            return self.create_form(request, school_id=school_id, student_id=student_id, pk=pk)
    def post(self, request, school_id=None, student_id=None, pk=None):
        return super().post(request, school_id, pk)


