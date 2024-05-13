
from django import forms
from datetime import datetime
from django.shortcuts import get_object_or_404


from django.db.models import Exists, OuterRef

from .models import (School, Student, Class, 
                     StudentClass, FinancialTransaction, Attendance)

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'description', 'image']
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
        fields = ['name', 'status', 'gender', 'date_of_birth', 'parents', 'phones', 'reward_points', 'note', 'image', 'classes']
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
    def __init__(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        super().__init__(*args, **kwargs)
        if school_id is not None:
            self.school_id = school_id
        else:
            self.school_id = None

    def get_classes(self):
        student_instance = self.instance
        print(student_instance)
        # Check if the student instance exists
        if not student_instance.pk:
            # The student isn't saved yet; return all classes from the specified school without extra processing
            return Class.objects.filter(school_id=self.school_id).order_by('-pk')

        # Annotate each class with a flag indicating if the student is in this class
        student_in_class_subquery = StudentClass.objects.filter(
            student=student_instance, _class=OuterRef('pk')
        )
        classes = Class.objects.filter(school_id=self.school_id).annotate(
            in_class=Exists(student_in_class_subquery)
        ).order_by('-in_class', '-pk')
        print(classes)
        # Convert the QuerySet to a list to avoid duplicate queries on iteration
        classes_list = list(classes)

        # Fetch all StudentClass instances for the current student to reduce query count
        student_classes = {sc._class_id: sc for sc in StudentClass.objects.filter(student=student_instance)}

        # Set `is_payment_required` on each class object
        for _class in classes_list:
            # Check if there's a StudentClass instance for this student and class
            student_class = student_classes.get(_class.id)
            if student_class:
                # Directly attach the is_payment_required attribute from StudentClass
                _class.is_payment_required = student_class.is_payment_required
            else:
                # Default to False if no StudentClass instance exists
                _class.is_payment_required = False

        return classes_list



class StudentNoteForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_note']
        widgets = {
            'last_note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_note = self.cleaned_data['last_note']
        current_date = datetime.now().strftime("- %d-%m-%Y %H:%M")
        if instance.note:
            instance.note = f'{current_date}: {new_note}\n' +  instance.note # Append the new note to the current note
            print(instance.note)
        else:
            instance.note = f'{current_date}: {new_note}'  # If there's no current note, set the new note
        instance.last_note = ""
        if commit:
            instance.save()
            print(instance.last_note)
        return instance



class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'price_per_hour', 'image',  'note', 'students']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Class name',
                'required': 'required',
                'class': 'form-input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input-file'
            }),
            'price_per_hour': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        super().__init__(*args, **kwargs)
        if school_id is not None:
            self.school_id = school_id
        else:
            self.school_id = None

    def get_students(self):
        class_instance = self.instance

        # Check if the class instance exists
        if not class_instance.pk:
            # The class isn't saved yet; return all students from the specified school without extra processing
            return Student.objects.filter(school_id=self.school_id).order_by('-pk')

        # Annotate each student with a flag indicating if they are in this class
        student_in_class_subquery = StudentClass.objects.filter(
            student=OuterRef('pk'), _class=class_instance
        )
        students = Student.objects.filter(school_id=self.school_id).annotate(
            in_class=Exists(student_in_class_subquery)
        ).order_by('-in_class', '-pk')

        # Convert the QuerySet to a list to avoid duplicate queries on iteration
        students_list = list(students)

        # Fetch all StudentClass instances for the current class to reduce query count
        student_classes = {sc.student_id: sc for sc in StudentClass.objects.filter(_class=class_instance)}

        # Set `is_payment_required` on each student object
        for student in students_list:
            # Check if there's a StudentClass instance for this student and class
            student_class = student_classes.get(student.id)
            if student_class:
                # Directly attach the is_payment_required attribute from StudentClass
                student.is_payment_required = student_class.is_payment_required
            else:
                # Default to False if no StudentClass instance exists
                student.is_payment_required = False

        return students_list



class AttendanceForm(forms.ModelForm):
    # form for attendance
    class Meta:
        model = Attendance
        fields = ['check_date', 'student', 'check_class', 'status', 'is_payment_required', 'use_price_per_hour_from_class', 'price_per_hour', 'learning_hours', 'note', ]
        widgets = {
            'check_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),

            'student': forms.Select(attrs={
                'class': 'form-input'
            }),

            'check_class': forms.Select(attrs={
                'class': 'form-input'
            }),
            'use_price_per_hour_from_class': forms.CheckboxInput(attrs={
                'class': 'checkbox'
            }),
            'is_payment_required': forms.CheckboxInput(attrs={
                'class': 'checkbox'
            }),

            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
            'learning_hours': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
            'price_per_hour': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
        }




class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['income_or_expense', 'transaction_type', 'giver', 'receiver', 'amount', 'student', 'bonus', 'student_balance_increase', 'created_at','note']
        widgets = {
            'income_or_expense': forms.Select(attrs={
                'class': 'form-input'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-input'
            }),
            'giver': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'receiver': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'created_at': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),

            'student': forms.Select(attrs={
                'class': 'form-input',
            }),

            'bonus': forms.Select(attrs={
                'class': 'form-input',
            }),

            'student_balance_increase': forms.NumberInput(attrs={
                'class': 'form-input',
            }),


        }

class TuitionPaymentForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['income_or_expense', 'transaction_type', 'student', 'receiver', 'amount', 'bonus', 'note']
        widgets = {
            'income_or_expense': forms.Select(attrs={
                'class': 'form-input disabled',
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'student': forms.Select(attrs={
                'class': 'form-input',
            }),
            'receiver': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'bonus': forms.Select(attrs={
                'class': 'form-input',
            }),

            'student_balance_increase': forms.NumberInput(attrs={
                'class': 'form-input',
            }),
            'created_at': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),

            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)
        if school_id is not None:
            self.school_id = school_id
            self.student_id = student_id
        else:
            self.school_id = None
            self.student_id = None

    def get_payments(self):
        payments = FinancialTransaction.objects.filter(school_id=self.school_id,student_id=self.student_id).order_by('created_at')
        return payments



class TuitionPaymentOldForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['income_or_expense', 'transaction_type', 'student', 'receiver', 'amount', 'note', 'student_balance_increase']
        widgets = {
            'income_or_expense': forms.Select(attrs={
                'class': 'form-input disabled',
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'student': forms.Select(attrs={
                'class': 'form-input',
            }),
            'receiver': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'amount': forms.Select(
                choices = [(0, "Chọn gói học phí"),
                           (1800000, "Quý 1.800.000 VNĐ (gốc)"),
                           (1620000, "Quý 1.620.000 VNĐ (gốc - 10%)"),
                           (1440000, "Quý 1.440.000 VNĐ (gốc - 20%)"),
                           (1350000, "Quý 1.350.000 VNĐ (gốc - 25%)"),
                           (1300000, "Quý 1.300.000 VNĐ (Hp chính sách cũ)"),
                           (3240000, "Nửa năm 3.240.000 VNĐ (gốc)"),
                           (2916000, "Nửa năm 2.916.000 VNĐ (gốc - 10%)"),
                           (5640000, "Năm 5.640.000 VNĐ (gốc)"),
                           (5076000, "Năm 5.076.000 VNĐ (gốc - 10%)"),],
                attrs={
                'class': 'form-input'
            }),

            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)
        if school_id is not None:
            self.school_id = school_id
            self.student_id = student_id
        else:
            self.school_id = None
            self.student_id = None

    def get_payments(self):
        payments = FinancialTransaction.objects.filter(school_id=self.school_id,student_id=self.student_id).order_by('created_at')
        return payments


class TuitionPaymentSpecialForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['income_or_expense', 'transaction_type', 'student', 'receiver', 'amount', 'student_balance_increase', 'note']
        widgets = {
            'income_or_expense': forms.Select(attrs={
                'class': 'form-input disabled',
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'student': forms.Select(attrs={
                'class': 'form-input',
            }),
            'receiver': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'student_balance_increase': forms.NumberInput(attrs={
                'class': 'form-input'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)
        if school_id is not None:
            self.school_id = school_id
            self.student_id = student_id
        else:
            self.school_id = None
            self.student_id = None

    def get_payments(self):
        payments = FinancialTransaction.objects.filter(school_id=self.school_id,student_id=self.student_id).order_by('created_at')
        return payments



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