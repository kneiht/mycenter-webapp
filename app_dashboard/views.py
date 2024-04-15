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
    SchoolForm, StudentForm, ClassForm, AttendanceForm, FinancialTransactionForm, TuitionPaymentForm
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

def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


# GENERAL PAGES ==============================================================
def landing_page(request):
    rendered_page = render(request, 'pages/single_page.html')
    return rendered_page

@login_required
def dashboard(request, school_id):
    school = School.objects.filter(pk=school_id).first()
    context = {'page': 'dashboard', 'title': 'Dashboard', 'school': school}
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


    return render(request, 'pages/single_page.html', context)

@login_required
def home(request):
    return redirect('schools')



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

    def post(self, request, school_id=None, pk=None):
        school = School.objects.filter(pk=school_id).first()
        if pk:
            instance = get_object_or_404(self.model_class, id=pk)
        result, instance, form = self.process_form(request, instance if pk else None)

        if result=='success':
            # add payment in students page
            if self.page=='students' and type(instance)==FinancialTransaction:
                instance = instance.student

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

        # Get the and sort option from the request
        sort_option = request.GET.get('sort', 'default')

        # Determine the fields to be used as filter options based on the selected page
        if self.page == 'schools':
            fields = ['all', 'name', 'description']
        elif self.page == 'students':
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
        if sort_option and hasattr(self.model_class, sort_option):
            records = records.order_by(sort_option)
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

        elif self.form_class==TuitionPaymentForm:
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
        else:
            form = self.form_class(instance=record) if record else self.form_class()
            record_id = record.pk if record else None


        html_modal = html_render('form', request, form=form, 
                                 modal=self.modal, record_id=record_id, 
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
                    if  self.model_class == Class:
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
            print(student)
            print(student.check_attendance(class_instance, check_date))
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
        } for record in attendance_records]
        return JsonResponse({'status': 'success', 'attendance_data': attendance_data})


    def update_class_attendance(self, request, school_id, pk):
        # Parsing the JSON data
        class_id = pk
        data = request.POST
        check_date_str = data.get('check_date')  # Assuming 'checkDate' is sent in the format 'YYYY-MM-DD HH:MM'
        learning_hours = data.get('learning_hours')
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
                            )

        # Process each status
        process_students('present', data.get('present', ''))
        process_students('absent', data.get('absent', ''))
        process_students('late', data.get('late', ''))
        process_students('left_early', data.get('left_early', ''))

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



class StudentAttendanceCalendarViewSet(BaseViewSet):
    model_class = Attendance
    form_class = AttendanceForm
    title =  'Manage Attendance'
    modal = 'modal_attendance'
    page = 'attendance'

    def get(self, request, school_id=None, student_id=None):
        return self.student_attendance_calendar(request, school_id, student_id)

    def student_attendance_calendar(self, request, school_id, student_id):
        student = get_object_or_404(Student, pk=student_id)
        payment_id = request.GET.get('payment_id')
        payments = FinancialTransaction.objects.filter(student=student).order_by('created_at')
        attendances = Attendance.objects.filter(student=student).order_by('check_date')
        
        if len(attendances)==0: #
            context = {
                'page': 'attendance',
                'title': 'Attendance - ' + student.name,
                'school': School.objects.filter(pk=school_id).first(),
                'student': student,
            }

            return render(request, 'pages/single_page.html', context)


        if not payment_id or payment_id=="all":
            # Assume we fetch the earliest and latest attendance dates for the student to define the range
            # For demonstration, replace these with actual queries if available
            earliest_attendance_date = Attendance.objects.filter(student=student).earliest('check_date').check_date
            latest_attendance_date = Attendance.objects.filter(student=student).latest('check_date').check_date

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
            for attendance in attendances:
                if attendance.is_payment_required:
                    cumulative_balance += attendance.price_per_hour * attendance.learning_hours

                if (cumulative_balance > balance_before_payment) and (cumulative_balance <= balance_up_to_payment):
                    filtered_attendance_ids.append(attendance.id)
                elif cumulative_balance > balance_up_to_payment:
                    break
            attendances = Attendance.objects.filter(id__in=filtered_attendance_ids)
            earliest_attendance_date = attendances.earliest('check_date').check_date
            latest_attendance_date = attendances.filter(student=student).latest('check_date').check_date

        # Adjust start_day and end_day to cover all attendance records
        start_day = earliest_attendance_date - timedelta(days=earliest_attendance_date.weekday())
        end_day = latest_attendance_date + timedelta(days=6 - latest_attendance_date.weekday())

        # Fetch attendances within the expanded date range
        attendances = Attendance.objects.filter(
            student=student,
            check_date__range=(start_day, end_day)
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
                'attendances': attendances_by_date.get(current_day.date(), [])
            }
            months[current_day.strftime("%Y-%m")]['days'].append(day_data)
            current_day += timedelta(days=1)

        # Convert months to a list if you want a sorted result
        months_list = [{'month': month, 'days': data['days']} for month, data in sorted(months.items())]

        context = {
            'page': 'attendance',
            'title': 'Attendance - ' + student.name,
            'school': School.objects.filter(pk=school_id).first(),
            'student': student,
            'months': months_list,
            'today': datetime.today(),
            'payments': payments,
            'selected_payment_id': payment_id,
        }

        return render(request, 'pages/single_page.html', context)




class FinancialTransactionViewSet(BaseViewSet):
    model_class = FinancialTransaction
    form_class = FinancialTransactionForm
    title =  'Manage Financial Transactions'
    modal = 'modal_financial_transaction'
    page = 'financial_transactions'

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



'''
@login_required
def classroom(request):
    #class_instance = Class.objects.get(pk=pk)
    # Retrieve students for the class
    #students_in_class = Student.objects.filter(studentclass___class=class_instance)
    inputs = { 
        'model': Student,
        'title': 'Manage Classroom',
        'select': 'classroom',
    }
    return list_records(request, **inputs)





# MANAGEMENT =================================================================
@login_required
def manage_other_models(request, model_name_plural):
    plural_singular_dict = {
        'students': 'student',
        'courses': 'course',
        'databasechangelogs': 'databasechangelog',
        'classschedules': 'classschedule',
        'tuitionplans': 'tuitionplan',
        'discounts': 'discount',
        'financialtransactions': 'financialtransaction',
        'userprofiles': 'userprofile',
        # Add other plural-to-singular mappings as needed
    }   
    model_name = plural_singular_dict[model_name_plural]


    admin_access_models = ['financialtransaction', 'databasechangelogs']
    # Check if the user is an admin
    if model_name in admin_access_models and not is_admin(request.user):
        return HttpResponseForbidden("Access restricted to admin users only.")

    model_class = apps.get_model(app_label='app_dashboard', model_name=model_name)

    # Extract field names
    field_names = [field.name for field in model_class._meta.get_fields()]

    # Exclude certain fields if necessary (e.g., id field)
    field_names = [name for name in field_names if name not in ['other_field_to_exclude']]

    context = {
        'model_name': model_name,
        'title': 'Manage ' + model_name_plural,
        'field_names': field_names,  # Add the field names to the context
    }

    return render(request, 'pages/manage_models.html', context)


# SPECIAL VIEWS
#------------------------------
@login_required
def form_generator(request):

    model_name = request.GET.get('model_name')
    id_record = request.GET.get('id_record')
    data = dict()

    # Mapping of model names to their respective forms
    form_classes = {
        'class': ClassForm,
        'student': StudentForm,
        'pay_tuition': PayTuitionForm,  # Assuming PayTuitionForm is defined elsewhere
        'attendance': AttendanceForm,
        'database_change_log': DatabaseChangeLogForm,
        'course': CourseForm,
        'classschedule': ClassScheduleForm,
        'daytime': DayTimeForm,
        'userprofile': UserProfileForm,
        'tuitionplan': TuitionPlanForm,
        'discount': DiscountForm,
        'financialtransaction': FinancialTransactionForm,
        # Add any additional model-to-form mappings as required
    }

    urls = {
        'class': reverse('class_list_create'),
        'student': reverse('student_list_create'),
        'course': reverse('course_list_create'),
        'classschedule': reverse('classschedule_list_create'),
        'tuitionplan': reverse('tuitionplan_list_create'),
        'discount': reverse('discount_list_create'),
        'attendance': reverse('attendance_list_create'),
        'financialtransaction': reverse('financialtransaction_list_create'),
        'transactionimage': reverse('transactionimage_list_create'),
        'pay_tuition': reverse('financialtransaction_list_create'),
        # Add any additional model-to-url mappings as required
    }

    # Fetch the form class based on the model_name parameter
    form_class = form_classes.get(model_name)

    urls.get(model_name)
    
    # If form_class exists and id_record is provided, fetch the instance and initialize the form
    if form_class and id_record:
        # financialtransaction model is used for 2 forms, payment and transaction
        if model_name=='pay_tuition':
            model_class = apps.get_model(app_label='app_dashboard', model_name='financialtransaction')
        else:
            model_class = apps.get_model(app_label='app_dashboard', model_name=model_name)


        instance = get_object_or_404(model_class, id=id_record)
        form = form_class(instance=instance)
        modal_name = 'Update information'
        is_new = False

    elif form_class:  # If no id_record is provided, provide an empty form
        if model_name in['pay_tuition', 'attendance']:
            student_id = request.GET.get('student_id')
            form = form_class(initial={'student': student_id})
        else:
            form = form_class()
        modal_name = 'Add new'
        is_new = True
    else:
        return JsonResponse({'error': 'Invalid model name'}, status=400)
    
    context = {
        'form': form, 
        'modal_name':  modal_name,
        'is_new': is_new,
        'id_record': id_record,
        'url_api': urls[model_name],
    }

    # Modal form for class is more complicated before it has students field
    # so we need to send students and the class instance to display
    if model_name=='class':
        context['is_class_modal_form'] = True
        context['students'] = Student.objects.all()
        if id_record:

            class_instance = get_object_or_404(Class, pk=id_record)
            context['class_instance'] = class_instance

            paid_class_students = StudentClass.objects.filter(_class=class_instance, is_paid_class=True)
            context['paid_class_students'] = [student_class.student for student_class in paid_class_students]

    elif model_name=='student':
        context['is_student_modal_form'] = True
        context['classes'] = Class.objects.all()
        if id_record:

            student = get_object_or_404(Student, pk=id_record)
            context['student'] = student

            paid_student_classes = StudentClass.objects.filter(student=student, is_paid_class=True)
            context['paid_classes'] = [student_class._class for student_class in paid_student_classes]

    elif model_name=="pay_tuition":
        context['is_pay_tuition_modal_form'] = True
        student_id = request.GET.get('student_id')

        student = get_object_or_404(Student, pk=student_id)
        previous_payments = FinancialTransaction.objects.filter(student=student)
        context['previous_payments'] = previous_payments

    elif model_name=="financialtransaction":
        context['is_financialtransaction_modal_form'] = True
        context['finance_image_form'] = TransactionImageForm()

    elif model_name=="attendance":
        context['is_attendance_modal_form'] = True


    data['html_modal'] = render_to_string('includes/elements/modal_form.html', context, request=request)
    return JsonResponse(data)











def calculate_paid_hour(student):
    total_paid_hours = FinancialTransaction.objects.filter(student=student).aggregate(total=Sum('tuition_plan__number_of_hours'))['total'] or 0
    total_paid_hours_used = Attendance.objects.filter(student=student, is_paid_class=True).aggregate(Sum('learning_hours'))
    total_paid_hours_used = total_paid_hours_used['learning_hours__sum'] or 0  # Returns 0 if the result is None
    
    student.total_paid_hours = total_paid_hours
    student.total_paid_hours_remaining = total_paid_hours - total_paid_hours_used
    student.total_paid_hours_used = total_paid_hours_used



@login_required
def fetch_one_record(request):
    model_name = request.GET.get('model_name')
    id_record = request.GET.get('id_record')
    model_class = apps.get_model(app_label='app_dashboard', model_name=model_name)

    record = get_object_or_404(model_class, id=id_record)

    context = {
        'model_name': model_name,
        'records': [record],  # Updated context
    }

    context['display_type'] = "card"
    html_card_content = render_to_string('includes/elements/data_lazy_loading.html', context, request)

    context['display_type'] = "table"
    html_table_content = render_to_string('includes/elements/data_lazy_loading.html', context, request)

    return JsonResponse({'html_card_content': html_card_content, 
        'html_table_content': html_table_content,})




@login_required
def fetch_records(request):
    model_name = request.GET.get('model_name')
    model_class = apps.get_model(app_label='app_dashboard', model_name=model_name)

    if model_name=="financialtransaction":
        records = model_class.objects.all().order_by('-create_date')
    elif model_name=="databasechangelog":
        records = model_class.objects.all().order_by('-change_date')
    else:
        records = model_class.objects.all().order_by('id')

    search_query = request.GET.get('search_query')
    if search_query:
        query = Q()
        for field in model_class._meta.get_fields():
            if hasattr(field, 'get_internal_type') and field.get_internal_type() in ['CharField', 'TextField']:
                # Apply icontains lookup on text-based fields
                query |= Q(**{f"{field.name}__icontains": search_query})
            elif isinstance(field, ForeignKey) or isinstance(field, ManyToManyField):
                # Handle ForeignKey and ManyToManyField fields
                for related_field in field.related_model._meta.fields:
                    if related_field.get_internal_type() in ['CharField', 'TextField']:
                        # Adding double underscore notation for related fields
                        query |= Q(**{f"{field.name}__{related_field.name}__icontains": search_query})
        records = records.filter(query).distinct() # Apply distinct to remove dups


    filter_str = request.GET.get('filter')
    if model_name=='student':
        for record in records:
            calculate_paid_hour(record)
            paid_student_classes = StudentClass.objects.filter(student=record, is_paid_class=True)
            record.paid_classes = [student_class._class for student_class in paid_student_classes]

        if filter_str == "debt_active":
            records = [record for record in records if record.total_paid_hours_remaining <= 0 and record.status == "enrolled"]
            records.sort(key=lambda x: x.total_paid_hours_remaining)

        elif filter_str == "debt_inactive":
            records = [record for record in records if record.total_paid_hours_remaining <= 0 and record.status != "enrolled"]
            records.sort(key=lambda x: x.total_paid_hours_remaining)

        elif filter_str == "active":
            records = [record for record in records if record.status == "enrolled"]
        elif filter_str == "inactive":
            records = [record for record in records if record.status != "enrolled"]

    elif model_name=='financialtransaction':
        TRANSACTION_TYPES = [
            'income_tuition_fee',
            'income_capital_contribution',
            'income_product_sales',
            'income_other_income',
            'expense_operational_expenses',
            'expense_asset_expenditure',
            'expense_marketing_expenses',
            'expense_salary_expenses',
            'expense_dividend_distribution',
            'expense_event_organization_expenses',
            'expense_human_resources_expenses',
            'expense_other_expenses'
        ]
        if filter_str in ["income", "expense"]:
            records = [record for record in records if record.income_or_expense == filter_str]

        elif filter_str in TRANSACTION_TYPES:
            records = [record for record in records if record.transaction_type == filter_str]




        if model_name == 'financialtransaction':
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if not start_date:
                # Set start_date to the earliest date in records
                earliest_date = min(record.create_date for record in records)
                start_date = earliest_date.strftime('%Y-%m-%d')

            if not end_date:
                # Set end_date to the latest date in records
                latest_date = max(record.create_date for record in records)
                end_date = latest_date.strftime('%Y-%m-%d')

            # Convert start_date and end_date to datetime objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Filter records
            records = [record for record in records if start_date <= record.create_date <= end_date]


        # Initialize total income, total expenses, and left variables
        total_income = 0.0
        total_expenses = 0.0

        # Calculate total income and total expenses while filtering by date
        for record in records:
            if record.income_or_expense == 'income':
                total_income += record.amount
            elif record.income_or_expense == 'expense':
                total_expenses += record.amount

        # Calculate the remaining balance
        remaining_balance = total_income - total_expenses

        # Print the results
        print(f'Total Income: {total_income}')
        print(f'Total Expenses: {total_expenses}')
        print(f'Remaining Balance: {remaining_balance}')


    # Pagination
    paginator = Paginator(records, 30)
    page = request.GET.get('page')
    try:
        paginated_records = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_records = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        #paginated_records = paginator.page(paginator.num_pages)
        return HttpResponse('') # Return nothing if last page


    # Determine if it's the last page
    is_last_page = paginated_records.number == paginator.num_pages


    context = {
        'model_name': model_name,
        'records': paginated_records,  # Updated context
        'is_last_page': is_last_page,
    }

    page = request.GET.get('page')




    context['display_type'] = "card"
    html_card_content = render_to_string('includes/elements/data_lazy_loading.html', context, request)

    context['display_type'] = "table"
    html_table_content = render_to_string('includes/elements/data_lazy_loading.html', context, request)


    if model_name == 'financialtransaction':
        return JsonResponse({'html_card_content': html_card_content, 
            'html_table_content': html_table_content, 
            'is_last_page': is_last_page,
            'filter_info': f"filter '{filter_str}' from {start_date} to {end_date}",
            'total_income': format_vnd(float(total_income)),
            'total_expenses': format_vnd(float(total_expenses)),
            'remaining_balance': format_vnd(float(remaining_balance))})
    else:
        return JsonResponse({'html_card_content': html_card_content, 
            'html_table_content': html_table_content, 
            'is_last_page': is_last_page,
            'filter_info': '',
            'total_income': '',
            'total_expenses': '',
            'remaining_balance': ''})


# CLASS MANAGEMENT VIEWS
#------------------------------
@login_required
def manage_classes(request):
    classes = Class.objects.all()
    context = {
        'classes': classes,
    }
    return render(request, 'manage/manage_classes.html', context)


@login_required
def manage_one_class(request, pk):
    class_instance = get_object_or_404(Class, pk=pk)
    students = class_instance.students.all()
    return render(request, 'manage/manage_one_class.html', {'class': class_instance, 'students': students})


@login_required
@csrf_exempt
def class_attendance(request, pk):
    class_id=pk
    if request.method == 'GET':
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'status': 'error', 'message': 'Date parameter missing.'})

        check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        attendance_records = Attendance.objects.filter(check_class=class_id, check_date__date=check_date).values('student_id', 'status')
        return JsonResponse({'status': 'success', 'data': list(attendance_records)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            attendance_data = data.get('attendance', [])
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

        for record in attendance_data:
            student_id = record.get('student_id')
            status = record.get('status')
            check_date_str = record.get('check_date')
            learning_hours = record.get('learning_hours')

            # Validate the input of each record
            if student_id is None or (status not in dict(Attendance.ATTENDANCE_STATUS) and status!='not_checked') or check_date_str is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid input'})
            
            # Validate date format
            try:
                check_date = datetime.strptime(check_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

            # Check paid class
            student = get_object_or_404(Student, pk=student_id)
            _class = get_object_or_404(Class, pk=class_id)
            paid_student_classes = StudentClass.objects.filter(student=student, _class=_class, is_paid_class=True)
            if len(paid_student_classes) != 0:
                is_paid_class = True
            else:
                is_paid_class = False


            if status == 'not_checked':
                # Delete the record if it exists
                records_to_delete = Attendance.objects.filter(student_id=student_id, check_class_id=class_id, check_date__date=check_date)
                records_to_delete.delete()
            else:
                existing_attendance = Attendance.objects.filter(
                    student_id=student_id,
                    check_class_id=class_id,
                    check_date__date=check_date,
                ).first()

                if existing_attendance:
                    # Update the existing record with the new status
                    existing_attendance.status = status
                    existing_attendance.create_date = timezone.now()
                    existing_attendance.is_paid_class = is_paid_class
                    existing_attendance.learning_hours = learning_hours
                    existing_attendance.save()

                else:
                    # Create a new attendance record
                    Attendance.objects.create(
                        student_id=student_id,
                        check_class_id=class_id,
                        check_date=check_date,
                        status=status,  
                        learning_hours=learning_hours,
                        is_paid_class=is_paid_class
                    )

        return JsonResponse({'status': 'success', 'message': 'Attendance updated successfully.'})

 
@login_required
@csrf_exempt
def add_money_to_students(request):
    if request.method == 'POST':
        # Parsing the JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        
        # Process the data
        for record in data:
            student_id = record['id']
            student_money_change = record['money']
            try:
                student = Student.objects.get(id=student_id)
                student.money += student_money_change
                student.save()
            except Student.DoesNotExist:
                pass

        # Return a success response
        return JsonResponse({'status': 'success', 'message': 'Students updated successfully'})

    # Return error response if not POST request
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




 


# ATTENDANCE VIEWS
#------------------------------

@login_required
def student_attendance_calendar(request, pk):
    student = get_object_or_404(Student, pk=pk)
    payments = FinancialTransaction.objects.filter(student=student).order_by('create_date')
    payment_id = request.GET.get('payment_id')

    attendances = Attendance.objects.filter(student=student).order_by('check_date')

    if payment_id and (payment_id !="unpaid"):
        selected_payment = get_object_or_404(FinancialTransaction, pk=payment_id)

        # Calculate the sum of learning hours up to and not including the selected payment
        paid_hours_before_payment = 0
        for payment in payments:
            if payment.create_date < selected_payment.create_date:
                paid_hours_before_payment += payment.tuition_plan.number_of_hours
                if payment == selected_payment:
                    break
        # Calculate the sum of learning hours up to and including the selected payment
        paid_hours_up_to_payment = paid_hours_before_payment + selected_payment.tuition_plan.number_of_hours

        # Filter attendances based on the cumulative hours
        cumulative_attendance_hours = 0
        filtered_attendance_ids = []
        for attendance in attendances:
            if attendance.is_paid_class:
                cumulative_attendance_hours += attendance.learning_hours

            if (cumulative_attendance_hours > paid_hours_before_payment) and (cumulative_attendance_hours <= paid_hours_up_to_payment):
                filtered_attendance_ids.append(attendance.id)
            elif cumulative_attendance_hours > paid_hours_up_to_payment:
                break
        attendances = Attendance.objects.filter(id__in=filtered_attendance_ids)

    elif payment_id == "unpaid":
        # Calculate the sum of learning hours up to and not including the selected payment
        total_paid_hours = 0
        for payment in payments:
            total_paid_hours += payment.tuition_plan.number_of_hours

        # Filter attendances based on the cumulative hours
        cumulative_attendance_hours = 0
        filtered_attendance_ids = []
        for attendance in attendances:
            if attendance.is_paid_class:
                cumulative_attendance_hours += attendance.learning_hours
            if cumulative_attendance_hours > total_paid_hours:
                filtered_attendance_ids.append(attendance.id)
        attendances = Attendance.objects.filter(id__in=filtered_attendance_ids)



    # Query your attendances and select_related or prefetch_related if needed
    attendances = attendances.order_by('check_date')
    #attendances_json = serialize('json', attendances.order_by('check_date'))

    # Use 'values' to get a dictionary with the fields you need
    attendances_list = list(attendances.values(
        'id', 'check_date', 'status', 'check_class__name', 'check_date', 'learning_hours', 'is_paid_class'
    ))
    
    # Convert the dictionary list to JSON
    attendances_json = json.dumps(attendances_list, cls=DjangoJSONEncoder)

    context = {
        'attendances_json': attendances_json,
        'student': student,
        'payments': payments,
        'selected_payment_id': payment_id,
    }

    context = {
        'attendances_json': attendances_json,  # Pass the serialized JSON to the context
        'student': student,
        'payments': payments,
        'selected_payment_id': payment_id,
    }

    return render(request, 'manage/manage_student_attendance_calendar.html', context)







# AJAX API ENDPOINTS
#------------------------------
def check_student_id(request):
    student_id = request.GET.get('id')
    exists = Student.objects.filter(id=student_id).exists()
    return JsonResponse({'exists': exists})

def fetch_payment_data(request, student_id):
    payments = Payment.objects.filter(student__id=student_id)       
    clean_data = []

    for payment in payments:
        clean_payment = {}
        
        clean_payment['number_of_lessons'] = payment.tuition_plan.number_of_lessons
        
        # Accessing other fields directly without serializing
        clean_payment['plan'] = payment.tuition_plan.plan
        clean_payment['final_fee'] = format_vnd(float(payment.final_fee))
        clean_payment['discount'] = payment.discount
        clean_payment['create_date'] = payment.create_date.strftime("%d/%m/%Y %H:%M")


        clean_payment['note'] = payment.note
        
        # Assuming you want to include the primary key as well in clean_data
        clean_payment['pk'] = payment.pk
        
        clean_data.append(clean_payment)

    #print(">>>> ", clean_data)
    
    return JsonResponse({'status': 'success', 'data': clean_data})
'''