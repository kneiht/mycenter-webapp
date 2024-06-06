


# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user

# Python Standard Library Imports


# Django and Other Third-Party Imports
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from app_dashboard.models import Student



# Using decorators to enforce authentication
def phone_number_in_session(view_func):
    def wrapped_view(request, *args, **kwargs):
        if 'phonenumber' not in request.session:
            return redirect('portal_login')
        return view_func(request, *args, **kwargs)
    return wrapped_view



def portal_login(request):
    # if user already logged in with the phone number, redirect to home page
    if 'phonenumber' in request.session:
        print (request.session['phonenumber'])
        if Student.objects.filter(phones__iexact=request.session['phonenumber']).exists():
            return redirect('portal_home')
        

    context = {'title': 'Đăng nhập'}
    # if post print data
    if request.method == 'POST':
        # Get phone number = username
        phone_number = request.POST.get('username')
        # Clean phone number
        phone_number = phone_number.replace('+84', '0')
        phone_number = phone_number.replace(' ', '')
        # Get student from phone number
        students = Student.objects.filter(phones__iexact=phone_number)
        if students:
            # Log in the user
            request.session['phonenumber'] = phone_number
            return redirect('portal_home')
        else:
            context['account_message'] = "Số điện thoại này chưa được đăng ký ghi danh tại anh ngữ GEN8. Vui lòng nhập đúng số điện thoại hoặc liên hệ ngữ GEN8 để được hỗ trợ."

    return render(request, 'portal/portal_login.html', context)




@phone_number_in_session
def portal_home(request):
    context = {'title': 'GEN8 Portal'}

    students = Student.objects.filter(phones__iexact=request.session['phonenumber'])
    if len(students) == 1:
        context['page'] = 'profile'
        context['student'] = students[0]
    else:
        context['page'] = 'select_students'
        context['students'] = students

    return render(request, 'portal/portal_home.html', context)


