
from django import forms
from .models import Student
from .models import Class
from .models import (
    Course, ClassSchedule, UserProfile,
    Class, TuitionPlan, Discount,
    Attendance, FinancialTransaction, Student
)

from .models import (BaseModel, DatabaseChangeLog, Course, 
    ClassSchedule, DayTime, UserProfile, Class, Student, 
    StudentClass, TuitionPlan, Discount, Attendance, 
    TransactionImage, FinancialTransaction)


from django.shortcuts import get_object_or_404
from django.forms import Widget

from .models import School

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'abbreviation', 'description', 'image']
        help_texts = {
            'abbreviation': 'This is used as a prefix to student ID',
        }

        widgets = {
            'name': forms.TextInput(attrs={
                    'placeholder': 'Your school name',
                    'required': 'required',
                    'class': 'form-input'}),
            'abbreviation': forms.TextInput(attrs={
                    'placeholder': 'Your school abbreviation',
                    'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                    'class': 'form-input', 
                    'rows': 2}),
            'image': forms.FileInput(attrs={
                    'class': 'form-input-file',}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'status', 'gender', 'date_of_birth', 'parents', 'phones', 'reward_points', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Student name',
                'required': 'required',
                'class': 'form-input'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-input'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'parents': forms.TextInput(attrs={
                'placeholder': 'Student parents',
                'class': 'form-input'
            }),
            'phones': forms.TextInput(attrs={
                'placeholder': 'Student phones',
                'class': 'form-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
            'reward_points': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input-file'
            }),
        }





'''

# CourseForm
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'books': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }

# DatabaseChangeLogForm
class DatabaseChangeLogForm(forms.ModelForm):
    class Meta:
        model = DatabaseChangeLog
        fields = '__all__'
        widgets = {
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'change': forms.TextInput(attrs={'class': 'form-control'}),
            'record_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'old_data': forms.Textarea(attrs={'class': 'form-control'}),
            'new_data': forms.Textarea(attrs={'class': 'form-control'}),
            'change_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

# ClassScheduleForm
class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'daytime': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }



# DayTimeForm
class DayTimeForm(forms.ModelForm):
    class Meta:
        model = DayTime
        fields = '__all__'
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }



# UserProfileForm
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# TuitionPlanForm
class TuitionPlanForm(forms.ModelForm):
    class Meta:
        model = TuitionPlan
        fields = '__all__'
        widgets = {
            'plan': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }

# DiscountForm
class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class StudentDisplayWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            student = Student.objects.get(pk=value)  # Replace 'Student' with your actual student model
            return f'<select name="student" class="form-control" id="id_student"><option value="{student.id}" data-price="0">{student.name}</option></select>'
        return '<input type="text" class="form-control" readonly value="No student assigned">'


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'check_class', 'check_date', 'status', 'learning_hours','note','is_paid_class']
        widgets = {
            'student': StudentDisplayWidget(),
            'check_class': forms.Select(attrs={'class': 'form-control'}),
            'check_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'learning_hours': forms.NumberInput(attrs={'class': 'form-control'}),

            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'is_paid_class': forms.CheckboxInput(attrs={'class': 'form-check-input-custom mx-3'}),
        }
        labels = {
            'check_class': 'Class',
            'check_date': 'Date',
            'status': 'Attendance Status',
            'learning_hours': 'Learning Hours',
            'is_paid_class': 'Is Paid Class',
            'note': 'Notes',
        }



class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'course', 'schedule', 'teacher', 'status', 'note', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'schedule': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=Class.CLASS_STATUS, attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            # Add any other form controls or widget customizations as needed
        }
        # If you want to customize the labels or help_texts, you can add:
        labels = {
            'note': 'Notes',
            # Add any other label customizations as needed
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'gender', 'date_of_birth', 'school', 'parents',
            'phone', 'status', 'note',
            'money', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'parents': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'money': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        # If you want to customize the labels or help_texts, you can add:
        labels = {
            'note': 'Notes',
            # Add any other label customizations as needed
        }





from django import forms
from django.forms.widgets import Select
from .models import FinancialTransaction, TuitionPlan
from .models import format_vnd

class TuitionPlanChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # This method dictates how the dropdown will display the options,
        # here it's assuming you want to show the name and the price of the tuition plan.
        return f"{obj.plan} - {str(format_vnd(obj.price))}"

class TuitionPlanSelectWidget(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        # Ensure we're dealing with a real object and not a 'ModelChoiceIteratorValue'


        if hasattr(value, 'instance'):
            tuition_plan = value.instance
            if tuition_plan:
                option['attrs']['data-price'] = tuition_plan.price
        elif type(value) == int:
            tuition_plan = get_object_or_404(TuitionPlan, pk=value)
            option['attrs']['data-price'] = tuition_plan.price

        return option

class DiscountSelectWidget(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        # Ensure we're dealing with a real object and not a 'ModelChoiceIteratorValue'
        print(value)
        if hasattr(value, 'instance'):
            discount = value.instance
            if discount:
                option['attrs']['data-discount-value'] = discount.discount_value
        elif type(value) == int:
            discount = get_object_or_404(Discount, pk=value)
            option['attrs']['data-discount-value'] = discount.discount_value


        return option

class DiscountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # This method dictates how the dropdown will display the options
        return f"{obj.name} - ({obj.discount_value * 100:.0f}%)"



from django.forms import Widget
class StudentDisplayWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            student = Student.objects.get(pk=value)  # Replace 'Student' with your actual student model
            return f'<select name="student" class="form-control" id="id_student"><option value="{student.id}" data-price="0">{student.name}</option></select>'
        return '<input type="text" class="form-control" readonly value="No student assigned">'


class PayTuitionForm(forms.ModelForm):

    # Define the hidden fields
    income_or_expense = forms.CharField(widget=forms.HiddenInput(), label='')
    transaction_type = forms.CharField(widget=forms.HiddenInput(), label='')


    tuition_plan = TuitionPlanChoiceField(
        queryset=TuitionPlan.objects.all(),
        widget=TuitionPlanSelectWidget(attrs={'class': 'form-control'}),
        label='Tuition Plan',
        empty_label=None,  # You can set this to 'Select tuition plan' or similar if you prefer
    )
    discount = DiscountChoiceField(
        queryset=Discount.objects.all(),
        widget=DiscountSelectWidget(attrs={'class': 'form-control'}),
        label='Discount',
        empty_label=None,
    )
    class Meta:
        model = FinancialTransaction
        fields = ['student', 'tuition_plan', 'discount', 'final_fee', 'note', 'create_date', 'income_or_expense', 'transaction_type']
        widgets = {
            'student': StudentDisplayWidget(),
            'final_fee': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'create_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'note': 'Notes',  # Customize the label as you see fit
            'final_fee': 'Final Fee',  # Example custom label
            # ... other labels as needed ...
        }


    def __init__(self, *args, **kwargs):
        super(PayTuitionForm, self).__init__(*args, **kwargs)
        # Set initial values for hidden fields if needed
        self.fields['income_or_expense'].initial = 'income'
        self.fields['transaction_type'].initial = 'income_tuition_fee'





class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = [
            'income_or_expense',
            'transaction_type',
            'permission_giver',
            'receiver',
            'amount',
            'student',
            'tuition_plan',
            'discount',
            'final_fee',
            'create_date',
            'note',
        ]
        widgets = {
            'income_or_expense': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'permission_giver': forms.Select(attrs={'class': 'form-control'}),
            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'tuition_plan': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.Select(attrs={'class': 'form-control'}),
            'final_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'create_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'note': 'Additional Notes',  # Customize the label as you see fit
            'amount': 'Transaction Amount',  # Example custom label
            # Add any other label customizations as needed
        }



class TransactionImageForm(forms.ModelForm):
    class Meta:
        model = TransactionImage
        fields = ['image']
        # You can add additional fields if needed

        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }


'''