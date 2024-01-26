# Python Standard Library Imports
import json
from datetime import datetime
import time

# Django and Other Third-Party Imports
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum  # 'Sum' is imported here

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


# Import forms
from .forms import (
    SchoolForm, StudentForm, 
)
# Import models
from django.contrib.auth.models import User
from .models import (
    School, Student, SchoolUser
)


def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


# GENERAL PAGES ==============================================================
def landing_page(request):
    rendered_page = render(request, 'pages/single_page.html')
    return rendered_page


@login_required
def dashboard(request, pk=None):
    request.user
    school = School.objects.get(pk=pk)
    context = { 
        'title': school.name,
        'page_title': 'Dashboard',
        'nav_bar': 'dashboard',
        'page_title': 'Dashboard',
        'title_bar': 'for_manage_schools',
        'school': school,
    }
    rendered_page = render(request, 'pages/single_page.html', context)
    return rendered_page


@login_required
def manage_schools(request):
    user = request.user
    # Filter the schools based on the user
    schools = School.objects.filter(users=user).order_by('-id')
    context = { 
        'records': schools,
        'title': 'Manage schools',
        'page_title': 'Manage schools',

        'nav_bar': 'for_manage_schools',
        'title_bar': 'for_manage_schools',
        'db_tool_bar': 'for_manage_schools',

        'card': 'card_school',
    }
    return render(request, 'pages/single_page.html', context)


# DATABASE MANAGEMENT VIEWS
#------------------------------
class BaseViewSet(viewsets.ModelViewSet):
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated]
    model_class = None
    form_class = None

    modal_selection = {
        School: 'modal_school',
        Student: 'modal_student',
    }
    card_selection ={
        School: 'card_school',
    }

    def process_form(self, request, instance=None):
        form = self.form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            if self.model_class == School:
                school_user = SchoolUser(school=instance, user=request.user)
                school_user.save()
            return 'success', instance, form
        else:
            return 'failed', instance, form

    def html_render(self, component, request, **kwargs):
        if component=='card':
            context = {
                    'record': kwargs.get('record'), 
                    'card': self.card_selection[self.model_class],
                    'swap_oob': 'hx-swap-oob="true"' if kwargs.get('swap_oob') else '',
            }
            template = 'components/card.html'

        elif component=='message':
            context = {
                    'modal': 'modal_message', 
                    'message': kwargs.get('message'),
                    'swap_oob': 'hx-swap-oob="true"',
            }
            template = 'components/modal.html'

        elif component=='form':
            context = {
                    'form': kwargs.get('form'), 
                    'modal': self.modal_selection[self.model_class],
                    'record_id': kwargs.get('record_id'),
                    'swap_oob': 'hx-swap-oob="true"',
            }
            template = 'components/modal.html'
        
        elif component=='display_cards':
            context = {
                    'records': kwargs.get('records'), 
                    'card': self.card_selection[self.model_class],
                    'swap_oob': 'hx-swap-oob="true"',
            }
            template = 'components/display_cards.html'

        return render_to_string(template, context, request)

    @action(detail=True, methods=['get'], url_path='form')
    def create_form(self, request, pk=None, *args, **kwargs):
        # Get the instance if pk is provided, use None otherwise
        record = self.model_class.objects.filter(pk=pk).first() if pk!='new' else None
        form = self.form_class(instance=record) if record else self.form_class()
        html_modal = self.html_render('form', request, form=form, record_id=record.pk if record else None)
        return HttpResponse(html_modal)
    

    def create(self, request, *args, **kwargs):
        result, instance, form = self.process_form(request)
        if result=='success':
            html_card = self.html_render('card', request, record=instance, swap_oob=False)
            html_message = self.html_render('message', request, message='create successfully')
            return HttpResponse(html_card + html_message)
        else:
            html_modal = self.html_render('form', request, form=form)
            return HttpResponse(html_modal)

    def update(self, request, *args, **kwargs):
        instance_id = kwargs.get('pk')
        instance = get_object_or_404(School, id=instance_id)
        result, instance, form = self.process_form(request, instance)
        if result=='success':
            html_card = self.html_render('card', request, record=instance, swap_oob=True)
            html_message = self.html_render('message', request, message='update successfully')
            return HttpResponse(html_card + html_message)
        else:
            html_modal = self.html_render('form', request, form=form, record_id=instance.pk)
            return HttpResponse(html_modal)


    def list(self, request, *args, **kwargs):
        # Get the and sort option from the request
        sort_option = request.GET.get('sort', 'name')

        # Get query parameters as lists
        descriptions = request.GET.getlist('description')
        names = request.GET.getlist('name')

        print(">>>> descriptions", descriptions)
        print(">>>> names", names)

        # Construct Q objects for filtering
        # Construct Q objects for filtering
        name_query = Q()
        for name in names:
            name_query |= Q(name__icontains=name)

        description_query = Q()
        for description in descriptions:
            description_query |= Q(description__icontains=description)

        # Combine queries with AND logic
        combined_query = Q()
        if name_query:
            combined_query &= name_query
        if description_query:
            combined_query &= description_query

        # Filter schools based on the query
        records = self.model_class.objects.filter(combined_query)

        # Sort the results
        if sort_option == 'name':
            records = records.order_by('name')
        elif sort_option == 'description':
            records = records.order_by('description')

        # Render the results
        context = {
            'records': records,
        }
        html = self.html_render('display_cards', request, records=records)
        return HttpResponse(html)


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


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'abbreviation', 'description']

class SchoolViewSet(BaseViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    model_class = School
    form_class = SchoolForm








'''
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