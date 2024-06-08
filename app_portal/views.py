


# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user

# Python Standard Library Imports


# Django and Other Third-Party Imports
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from app_dashboard.models import Student
from django.db.models import Q



def filter_students_by_phone_number(phone_number):
    students = Student.objects.filter(
            Q(mother_phone__iexact=phone_number) |
            Q(father_phone__iexact=phone_number)
        )
    return students

# Using decorators to enforce authentication
def phone_number_in_session(view_func):
    def wrapped_view(request, *args, **kwargs):
        if 'phonenumber' not in request.session:
            return redirect('portal_login') 
        return view_func(request, *args, **kwargs)
    return wrapped_view



def portal_login(request):

    context = {
        'page': 'login', 
        'title': 'Đăng nhập',}
    # if post print data
    if request.method == 'POST':
        # Get phone number = username
        phone_number = request.POST.get('username')
        # Clean phone number
        phone_number = phone_number.replace('+84', '0')
        phone_number = phone_number.replace(' ', '')
        # Get student from phone number
        students = filter_students_by_phone_number(phone_number)
        if students:
            # Log in the user
            request.session['phonenumber'] = phone_number
            return redirect('portal_profile')
        else:
            context['account_message'] = "Số điện thoại này chưa được đăng ký ghi danh tại anh ngữ GEN8. Vui lòng nhập đúng số điện thoại hoặc liên hệ ngữ GEN8 để được hỗ trợ."
    else:
        # if user already logged in with the phone number, redirect to home page
        if 'phonenumber' in request.session:
            print (request.session['phonenumber'])
            if request.session['phonenumber']:
                students = filter_students_by_phone_number(request.session['phonenumber'])
                if students.exists():
                    return redirect('portal_profile')

    
    return render(request, 'portal/portal_login.html', context)


def portal_logout(request):
    # if user already logged in with the phone number, redirect to home page
    if 'phonenumber' in request.session:
        print(1)
        if request.session['phonenumber']:
            print(2)
            request.session['phonenumber'] = None
    return redirect('portal_login')

@phone_number_in_session
def portal_app(request):
    context = {'title': 'GEN8 Portal',
               'page': 'app'}
    return render(request, 'portal/portal_app.html')



@phone_number_in_session
def portal_profile(request):
    context = {'title': 'GEN8 Portal'}
    students = filter_students_by_phone_number(request.session['phonenumber'])
    
    
    context['page'] = 'profile'
    context['student'] = students[0]

    return render(request, 'portal/portal_profile.html', context)

@phone_number_in_session
def portal_calendar(request):
    return render(request, 'portal/portal_calendar.html', context)

@phone_number_in_session
def portal_zalo(request):
    return render(request, 'portal/portal_zalo.html', context)



