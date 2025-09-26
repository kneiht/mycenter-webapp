import time    
from django.core.exceptions import ValidationError

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import re
from django.db import IntegrityError

from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.db.models.fields.files import ImageFieldFile
from datetime import datetime, date
import json
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User

from django.db.models import Max
from django.db import transaction
from django.db.models import Q, Count, Sum, F, FloatField  # 'Sum' is imported here



class BaseModel(models.Model):
    last_saved = models.DateTimeField(default=timezone.now, blank=True, null=True)
    class Meta:
        abstract = True  # Specify this model as Abstract

    def compress_image(self, image_field, max_width):
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found

        if '_compressed' in image_field.name:
            return image_field

        # Resize the image if it is wider than 600px
        if image_temp.width > max_width:
            # Calculate the height with the same aspect ratio
            height = int((image_temp.height / image_temp.width) * max_width)
            image_temp = image_temp.resize((max_width, height), Image.Resampling.LANCZOS)

        # Define the output stream for the compressed image
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=40)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "%s_compressed.webp" % image_field.name.split('.')[0]
        #print('\n\n\n>>>>>' , file_name)
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)
        
        return output_imagefield

    def create_thumbnail(self, image_field):
        max_width = 60
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found

        height = int((image_temp.height / image_temp.width) * max_width)
        image_temp = image_temp.resize((max_width, height), Image.Resampling.LANCZOS)
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=40)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "%s.thumbnail" % image_field.name.split('.')[0]
        #print('>>>>>' , file_name)
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)

        return output_imagefield


    def save(self, *args, **kwargs):
        # refine fields
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to compress
                    #print('\n\ncompressed')
                    compressed_image = self.compress_image(value, 500)
                    setattr(self, field.name, compressed_image)

                    if not Thumbnail.objects.filter(reference_url=value.url).exists():
                        thumbnail_image = self.create_thumbnail(value)
                        thumbnail = Thumbnail.objects.create(
                            reference_url=value.url,
                            thumbnail=None
                        )
                        setattr(thumbnail, 'thumbnail', thumbnail_image)
                        thumbnail.save()

            elif isinstance(value, str):
                # Remove leading and trailing whitespaces
                value = value.strip()
                # Replace multiple spaces with a single space
                value = re.sub(r' +', ' ', value)
                setattr(self, field.name, value)

        # Save the current instance
        self.last_saved = timezone.now()
        
        super().save(*args, **kwargs)

        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to create thumbnail
                    if not Thumbnail.objects.filter(reference_url=value.url).exists():
                        thumbnail_image = self.create_thumbnail(value)
                        thumbnail = Thumbnail.objects.create(
                            reference_url=value.url,
                            thumbnail=None
                        )
                        setattr(thumbnail, 'thumbnail', thumbnail_image)
                        thumbnail.save()



class SecondaryIDMixin(models.Model):
    secondary_id = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = True  # This makes it a mixin, not a standalone model

    def save(self, *args, **kwargs):
        if self._state.adding and hasattr(self, 'school'):
            with transaction.atomic():
                highest_id = self.__class__.objects.filter(
                    school=self.school
                ).aggregate(max_secondary_id=Max('secondary_id'))['max_secondary_id'] or 0
                self.secondary_id = highest_id + 1
        super().save(*args, **kwargs)

class Thumbnail(models.Model):
    reference_url = models.CharField(max_length=255, blank=True, null=True)
    thumbnail  = models.ImageField(upload_to='images/thumbnails/', blank=True, null=True)



class School(BaseModel):
    moved_to_trash = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, default='')
    image = models.ImageField(upload_to='images/schools/', blank=True, null=True, default='images/default/default_school.webp')
    users = models.ManyToManyField(User, through='SchoolUser')
    zalo = models.CharField(max_length=255, default="No zalo", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class SchoolUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    GENDER_CHOICES = (("Male", "Male"), ("Female", "Female"), ("Other", "Other"))
    name = models.CharField(max_length=255, default="Unspecified")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="other")
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(default="", blank=True)
    image = models.ImageField(upload_to='images/profiles/', blank=True, null=True, default='images/default/default_profile.webp')
    settings = models.ForeignKey('FilterValues', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class FilterValues(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    filter = models.CharField(max_length=255, default="nothing to filter")
    value = models.TextField(default="", blank=True)
    def __str__(self):
        return self.filter

class Student(SecondaryIDMixin, BaseModel):
    GENDER_CHOICES = (("male", "Male"), ("female", "Female"), ("other", "Other"))
    STUDENT_STATUS = (
        ('enrolled', 'Enrolled'),                 # Student is currently enrolled
        ('free_tuition', 'Free Tuition'),                 # Student is currently enrolled
        ('on_hold', 'On Hold'),                   # Student is on hold
        ('discontinued', 'Discontinued'),         # Student has discontinued
    )
    CRM_STATUS = (
        ('potential_customer', 'Potential'),  # Potential customer with potential interest
        ('not_contacted_customer', 'Not Contacted'), # Customer not contacted yet
        ('not_potential_customer', 'Not Potential'), # Not a potential customer
        ('just_added', 'Just Added'), # Not a potential customer
        ('archived', 'Archived'),
    )
    # combine 2  status
    STATUS_CHOICES = list(STUDENT_STATUS) + list(CRM_STATUS)
    moved_to_trash = models.BooleanField(default=False)
    student_id = models.IntegerField(blank=True, null=True)
    is_converted_to_student = models.BooleanField(default=False, blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    classes = models.ManyToManyField('Class', through='StudentClass', blank=True)
    name = models.CharField(max_length=255, default="")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="other")
    date_of_birth = models.DateField(null=True, blank=True)
    mother = models.CharField(max_length=255, default="", blank=True, null=True)
    mother_phone = models.CharField(max_length=50, default="", blank=True, null=True)

    father = models.CharField(max_length=255, default="", blank=True, null=True)
    father_phone = models.CharField(max_length=50, default="", blank=True, null=True)
    
    address = models.TextField(default="Chưa có địa chỉ", blank=True, null=True)

    status =  models.CharField(max_length=50, choices=STATUS_CHOICES, default="potential_customer")
    reward_points = models.IntegerField(default=0, blank=True)
    balance = models.FloatField(default=0, blank=True)
    image = models.ImageField(upload_to='images/profiles/', blank=True, null=True, default='images/default/default_profile.webp')
    image_portrait = models.ImageField(upload_to='images/portraits/', blank=True, null=True, default='images/default/default_profile.webp')
    note = models.TextField(default="", blank=True, null=True)
    last_note = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.name)
    

    def calculate_student_balance(self):
        # Summarize all student_balance_increase from FinancialTransaction
        total_increase = FinancialTransaction.objects.filter(student=self).aggregate(Sum('student_balance_increase'))['student_balance_increase__sum'] or 0
        # Calculate total attendance cost
        total_attendance_cost = Attendance.objects.filter(student=self, is_payment_required=True).annotate(
            total_cost=Sum(F('learning_hours') * F('price_per_hour'), output_field=FloatField())
        ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0
        # Calculate final balance
        self.balance = total_increase - total_attendance_cost
        self.save()
        #print('\n\n>>>>>>', self.balance)


    def save(self, *args, **kwargs):
        if self.mother_phone is None:
            self.mother_phone = ""
        self.mother_phone = str(self.mother_phone).replace(" ", "")
        self.mother_phone = str(self.mother_phone).replace(".", "")

        if self.father_phone is None:
            self.father_phone = ""
        self.father_phone = str(self.father_phone).replace(" ", "")
        self.father_phone = str(self.father_phone).replace(".", "")

        if self.is_converted_to_student:
            if self.status not in ['enrolled', 'on_hold', 'discontinued', 'free_tuition']:
                self.status = "enrolled"

        if not self.student_id and self.is_converted_to_student and hasattr(self, 'school'):
            with transaction.atomic():
                highest_id = self.__class__.objects.filter(
                    school=self.school
                ).aggregate(max_student_id=Max('student_id'))['max_student_id'] or 0
                self.student_id = highest_id + 1
        super().save(*args, **kwargs)

    def get_student_classes(self):
        classes = StudentClass.objects.filter(student=self)
        return classes


    def check_attendance(self, check_class, check_date):
        if type(check_date) == str:
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        attendance = Attendance.objects.filter(
            student=self, 
            check_class=check_class, 
            check_date__date=check_date  # Extract date part
        ).first()        
        if attendance and attendance.status in ['present', 'late', 'left_early']:
            return True
        else:
            return False


class TimeFrame(models.Model):
    time_frame = models.CharField(max_length=255, default="", blank=True, null=True)
    def __str__(self):
        return self.time_frame

class Class(SecondaryIDMixin, BaseModel):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('archived', 'Archived'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    moved_to_trash = models.BooleanField(default=False)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, default="New class")
    students = models.ManyToManyField('Student', through='StudentClass', blank=True)
    image = models.ImageField(upload_to='images/classes/', blank=True, null=True, default='images/default/default_class.webp')
    price_per_hour =  models.IntegerField(default=0, null=True, blank=True)
    note = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    # Add time_frame to class by foreign key TimeFrame
    time_frame = models.ForeignKey(TimeFrame, on_delete=models.SET_NULL, null=True, blank=True)
    zalo = models.CharField(max_length=255, default="No zalo", blank=True, null=True)

    def __str__(self):
        return f"{str(self.name)}"
    def get_student_number(self):
        return self.students.count()

    def get_charge_student_number(self):
        return StudentClass.objects.filter(_class=self, student__in=self.students.all(), is_payment_required=True).count()
    
    def get_current_students(self):
        """Get all students currently in this class"""
        return self.students.filter(moved_to_trash=False)


class StudentClass(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    _class = models.ForeignKey('Class', on_delete=models.CASCADE)
    is_payment_required = models.BooleanField(default=True)
    class Meta:
        unique_together = ('student', '_class')

    def __str__(self):
        return f"{self.student.name} - {self._class.name}"
    

    def class_name(self):
        return self._class.name

    def get_class(self):
        return self._class

class Attendance(SecondaryIDMixin, BaseModel):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('late', 'Late'),
        ('left_early', 'Left Early'),
        ('absent', 'Absent'),
        ('not_checked', 'Not Checked'),
    )
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    check_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    check_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")
    learning_hours = models.FloatField(default=1.5, null=True, blank=True)
    use_price_per_hour_from_class = models.BooleanField(default=True)
    price_per_hour = models.IntegerField(default=0, null=True, blank=True)
    is_payment_required = models.BooleanField(default=None, null=True, blank=True)
    note = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.status == 'not_checked':
            self.is_payment_required = False
        self.learning_hours = float(self.learning_hours)
        # Set the microsecond part to zero before saving
        if self.check_date:
            #handle the case 2024-04-19T16:55:38
            if "T" in str(self.check_date):
                self.check_date = datetime.strptime(str(self.check_date), '%Y-%m-%dT%H:%M:%S')
            else:
                self.check_date = datetime.strptime(str(self.check_date), '%Y-%m-%d %H:%M:%S')
            self.check_date = self.check_date.replace(microsecond=0)


        if self.use_price_per_hour_from_class and self.check_class:
            self.price_per_hour = self.check_class.price_per_hour

        # get is_payment_required from the StudentClass
        if self.is_payment_required is None:
            if self.student and self.check_class:
                try:
                    student_class = StudentClass.objects.get(student=self.student, _class=self.check_class)
                    self.is_payment_required = student_class.is_payment_required
                except StudentClass.DoesNotExist:
                    self.is_payment_required = True
        else:
            self.is_payment_required = self.is_payment_required
        
        # If the attendance is being created, updated, or deleted, update the student's balance
        if self.student and self.is_payment_required:
            if self._state.adding:
                self.student.balance = self.student.balance - self.price_per_hour * self.learning_hours
            else:
                # Fetch the old learning hours and old_price_per_hour
                old_attendance = Attendance.objects.get(pk=self.pk)
                old_learning_hours = old_attendance.learning_hours
                old_price_per_hour = old_attendance.price_per_hour
                # Update the balance
                self.student.balance = self.student.balance + old_price_per_hour * old_learning_hours - self.price_per_hour * self.learning_hours
            self.student.save()
        super(Attendance, self).save(*args, **kwargs)
        self.student.calculate_student_balance()


    def delete(self, *args, **kwargs):
        if self.student and self.is_payment_required:
            self.student.balance = self.student.balance + self.price_per_hour * self.learning_hours
            self.student.save()
        super().delete(*args, **kwargs)  # Perform the actual database deletion
        self.student.calculate_student_balance()

        # Custom logic after deletion (optional)
        # ...

    def __str__(self):
        return "{} - {} - {} - {}".format(str(self.student), str(self.check_class), str(self.check_date), str(self.is_payment_required), str(self.status))



class FinancialTransaction(SecondaryIDMixin, BaseModel):
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    IN_OR_OUT_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    STATUS_CHOICES = (
        ('checked', 'Checked'),
        ('unchecked', 'Unchecked'),
        ('suspect', 'Suspect'),
    )

    TRANSACTION_INCOME_TYPES = (
        ('income_tuition_fee', 'In - Tuition'),
        ('income_capital_contribution', 'In - Capital'),
        ('income_product_sales', 'In - Product Sales'),
        ('income_other_income', 'In - Other Income'),
    )
    TRANSACTION_EXPENSE_TYPES = (
        ('expense_operational_expenses', 'Exp - Operation'),
        ('expense_asset_expenditure', 'Exp - Assets'),
        ('expense_marketing_expenses', 'Exp - Marketing'),
        ('expense_salary_expenses', 'Exp - Salary'),
        ('expense_dividend_distribution', 'Exp - Dividend'),
        ('expense_event_organization_expenses', 'Exp - Events'),
        ('expense_human_resources_expenses', 'Exp - HR'),
        ('expense_other_expenses', 'Exp - Other'),
    )
    TRANSACTION_TYPES = list(TRANSACTION_INCOME_TYPES) + list(TRANSACTION_EXPENSE_TYPES)

    income_or_expense = models.CharField(max_length=20, choices=IN_OR_OUT_CHOICES)
    status =  models.CharField(max_length=50, choices=STATUS_CHOICES, default="unchecked")
    transaction_type = models.CharField(max_length=255, choices=TRANSACTION_TYPES)
    giver = models.CharField(max_length=100, default="Không xác định", null=True, blank=True)
    receiver = models.CharField(max_length=100, default="Không xác định", null=True, blank=True)
    amount = models.FloatField(default=0, null=True, blank=True)

    # fields for tuition payments
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    student_balance_increase = models.FloatField(default=0, null=True, blank=True)
    legacy_discount = models.TextField(default="", blank=True, null=True)
    legacy_tuition_plan = models.TextField(default="", blank=True, null=True)
    last_note = models.TextField(default="", blank=True, null=True)
    note = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    image1 = models.ImageField(upload_to='images/transactions/', blank=True, null=True, default='images/default/default_transaction.webp')
    image2 = models.ImageField(upload_to='images/transactions/', blank=True, null=True, default='images/default/default_transaction.webp')
    image3 = models.ImageField(upload_to='images/transactions/', blank=True, null=True, default='images/default/default_transaction.webp')
    image4 = models.ImageField(upload_to='images/transactions/', blank=True, null=True, default='images/default/default_transaction.webp')
    image5 = models.ImageField(upload_to='images/transactions/', blank=True, null=True, default='images/default/default_transaction.webp')

    def __str__(self):
        return self.get_transaction_type_display()

    def save(self, *args, **kwargs):
        # The balance is calculated based on the transaction type
        if self.transaction_type=='income_tuition_fee' and self.student and self.amount: 

            if self._state.adding: # If the transaction is being created
                self.income_or_expense = 'income'
                self.giver = self.student.name
                self.receiver = self.school.name
                self.student.balance = self.student.balance + self.student_balance_increase
            else: # If the transaction is being updated
                # Fetch the old amount
                old_student_balance_increase = FinancialTransaction.objects.get(pk=self.pk).student_balance_increase
                # Update the balance
                if not old_student_balance_increase:
                    old_student_balance_increase = 0   
                self.student.balance = float(self.student.balance) - float(old_student_balance_increase) + float(self.student_balance_increase)
            
            self.student.save()
        
        # If the transaction is not tuition fee, remove the student_balance_increase, and student
        if self.transaction_type != 'income_tuition_fee' and self.student:
            self.student_balance_increase = 0
            self.student = None

            
        super().save(*args, **kwargs)
        if self.transaction_type=='income_tuition_fee' and self.student:
            self.student.calculate_student_balance()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.transaction_type == 'income_tuition_fee' and self.student:
            self.student.calculate_student_balance()

    def clean(self):
        errors = ""
        if self.amount is not None and self.amount < 0:
            errors += "- Amount không được âm.\n"
        if self.student_balance_increase is not None and self.student_balance_increase < 0:
            errors += "- Balance increase không được âm.\n"
        # Add rule: income_or_expense must match transaction_type
        income_types = [t[0] for t in self.TRANSACTION_INCOME_TYPES]
        expense_types = [t[0] for t in self.TRANSACTION_EXPENSE_TYPES]
        if self.income_or_expense == 'income' and self.transaction_type not in income_types:
            errors += "- Transaction type does not match 'income'.\n"
        if self.income_or_expense == 'expense' and self.transaction_type not in expense_types:
            errors += "- Transaction type does not match 'expense'.\n"
        if errors:
            raise ValidationError(errors)



class Announcement(BaseModel):

    title = models.CharField(max_length=255, verbose_name="Title")
    note = models.TextField(verbose_name="Content", default="", blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="User"
    )
    publish_date = models.DateTimeField(verbose_name="Publish Date", default=timezone.now)
    attachment = models.FileField(
        upload_to="announcements/", verbose_name="Attachment", null=True, blank=True
    )
    is_pinned = models.BooleanField(default=False, verbose_name="Pinned")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        ordering = ["-is_pinned", "-publish_date"]

    def __str__(self):
        return str(self.title) + "- " + str(self.user) + " - " + str(self.publish_date)

    def save(self):
        print(self.note)
        # Skip if user changed (keep first user)
        if self.pk:
            old_instance = Announcement.objects.get(pk=self.pk)
            if old_instance.user:
                self.user = old_instance.user
        super().save()



class TuitionPlan(models.Model):
    name = models.CharField(max_length=255, default="", blank=True, null=True, unique=True)
    amount = models.FloatField(default=0, null=True, blank=True)
    balance_increase = models.FloatField(default=0, null=True, blank=True)
    def __str__(self):
        return self.name + " - " + str(self.amount)
    
    @staticmethod
    def to_amount_selections():
        return [(plan.amount, plan.name) for plan in TuitionPlan.objects.all()]

    @staticmethod
    def to_amount_and_balance_increase_selections():
        # plan dict
        plans = []
        for plan in TuitionPlan.objects.all():
            plans.append({
                "name": plan.name,
                "amount": plan.amount,
                "balance_increase": plan.balance_increase
            })
        # convert to json
        return plans


class Examination(SecondaryIDMixin, BaseModel):
    """
    Model representing an exam column (e.g., Mid-term Test, Final Test, Quiz 1, etc.)
    Each examination belongs to a specific class in a specific school
    """
    EXAM_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('homework', 'Homework'),
        ('midterm', 'Mid-term Test'),
        ('final', 'Final Test'),
        ('project', 'Project'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=255, verbose_name='Examination Name')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='quiz', verbose_name='Exam Type')
    date = models.DateField(verbose_name='Date of Examination', null=True, blank=True)
    note = models.TextField(blank=True, null=True, verbose_name='Note')
    examination_class = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='examinations', verbose_name='Class')
    school = models.ForeignKey('School', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    default_score = models.FloatField(default=0.0, verbose_name='Default Score')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['examination_class', 'name']  # Prevent duplicate exam names in same class
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.examination_class.name}"
    
    def get_all_student_scores(self):
        """Get all student scores for this examination"""
        return StudentExamination.objects.filter(examination=self)
    
    def get_students_with_scores(self):
        """Get all students in the class with their scores for this exam"""
        students = self.examination_class.get_current_students()
        scores_data = []
        
        for student in students:
            try:
                score = StudentExamination.objects.get(student=student, examination=self).score
            except StudentExamination.DoesNotExist:
                score = self.default_score
            
            scores_data.append({
                'student': student,
                'score': score
            })
        
        return scores_data


class StudentExamination(BaseModel):
    """
    Model representing a student's score for a specific examination
    This preserves scores even if student is removed from class
    """
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='exam_scores')
    examination = models.ForeignKey('Examination', on_delete=models.CASCADE, related_name='student_scores')
    score = models.FloatField(verbose_name='Score')
    note = models.TextField(blank=True, null=True, verbose_name='Note')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = [('student', 'examination')]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.examination.name}: {self.score}"
    
    @property
    def score_color_class(self):
        """Return CSS class based on score range"""
        if self.score >= 8:
            return 'bg-green-100 text-green-800'
        elif self.score >= 5:
            return 'bg-yellow-100 text-yellow-800'
        else:
            return 'bg-red-100 text-red-800'