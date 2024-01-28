

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


from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    image = models.ImageField(upload_to='images/schools/', blank=True, null=True, default='images/default/default_school.webp')
    users = models.ManyToManyField(User, through='SchoolUser')
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
    settings = models.ForeignKey('KeyValue', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class KeyValue(models.Model):
    key = models.CharField(max_length=255, default="")
    value = models.CharField(max_length=255, default="")
    def __str__(self):
        return self.key

class Student(models.Model):
    GENDER_CHOICES = (("male", "Male"), ("female", "Female"), ("other", "Other"))
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    classes = models.ManyToManyField('Class', through='StudentClass', blank=True)
    name = models.CharField(max_length=255, default="")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="other")
    date_of_birth = models.DateField(null=True, blank=True)
    parents = models.CharField(max_length=255, default="", blank=True, null=True)
    phones = models.CharField(max_length=50, default="", blank=True, null=True)
    status =  models.CharField(max_length=50, default="New", blank=True, null=True)
    reward_points = models.IntegerField(default=0, blank=True)
    image = models.ImageField(upload_to='images/profiles/', blank=True, null=True, default='images/default/default_profile.webp')
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.name)


class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, default="New class")
    students = models.ManyToManyField('Student', through='StudentClass', blank=True)
    image = models.ImageField(upload_to='images/classes/', blank=True, null=True, default='images/default/default_class.webp')
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{str(self.name)}"


class StudentClass(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    _class = models.ForeignKey('Class', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', '_class')

    def __str__(self):
        return f"{self.student.name} - {self._class.name}"









class Course(models.Model):
    name = models.CharField(max_length=255, default="")
    hours = models.FloatField(default=0, null=True, blank=True)
    books = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name



class ClassSchedule(models.Model):
    name = models.CharField(max_length=255, default="")
    daytime = models.ManyToManyField('DayTime')

    def __str__(self):
        return self.name


class DayTime(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"
















def format_vnd(amount):
    # Convert the number to a string and reverse it
    amount_str = str(int(amount))[::-1]
    
    # Insert a dot every 3 digits
    formatted_str = '.'.join(amount_str[i:i+3] for i in range(0, len(amount_str), 3))
    
    # Reverse the string back and append the VND symbol
    return formatted_str[::-1] + " VNĐ"


class BaseModel(models.Model):
    class Meta:
        abstract = True  # Specify this model as Abstract

    def compress_image(self, image_field):
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found


        # Get the size of the original image in kilobytes
        original_io_stream = io.BytesIO()
        image_field.seek(0)  # Go to the beginning of the file-like object
        original_io_stream.write(image_field.read())  # Write image data to the new stream to check size
        original_size_kb = original_io_stream.tell() / 1024  # Size in KB
        
        # Check if the original image size is less than 20KB, return the original image
        print('\n\n>>>>>', original_size_kb)
        if original_size_kb < 20 or 'servercompressed' in image_field.name:
            return image_field

        # Resize the image if it is wider than 600px
        if image_temp.width > 600:
            # Calculate the height with the same aspect ratio
            height = int((image_temp.height / image_temp.width) * 600)
            image_temp = image_temp.resize((600, height), Image.Resampling.LANCZOS)

        # Define the output stream for the compressed image
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=40)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "servercompressed%s.webp" % image_field.name.split('.')[0]
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)
        return output_imagefield


    def get_serializable_data(self):
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                data[field.name] = value.url if value else None
            elif isinstance(value, datetime):
                data[field.name] = value.isoformat() if value else None

            elif isinstance(value, date):
                data[field.name] = value.isoformat() if value else None

            elif isinstance(value, models.Model):
                # For foreign key relations, you can choose to serialize only the ID or the entire object
                #print(value)
                data[field.name] = value.id
            else:
                data[field.name] = value
        return data


    def log_change(self, action, old_data=None, new_data=None):
        if old_data and new_data:
            # Determine which fields have changed
            changed_fields = {field for field in new_data if new_data[field] != old_data[field] and (
                (new_data[field] is not None and new_data[field] != "") or
                (old_data[field] is not None and old_data[field] != "")
            )}
            
            if not changed_fields:
                # If no fields have changed, do not log
                return

            if changed_fields == {'money'}:
                # If only the excluded field has changed, do not log
                return
        else:
            if old_data:
                changed_fields = {field for field in old_data}
            else:
                changed_fields = {field for field in new_data}

        if self.__class__.__name__ != 'DatabaseChangeLog':  # Avoid recursion
            DatabaseChangeLog.objects.create(
                model_name=self.__class__.__name__,
                change=action,
                record_id=self.id,
                old_data=json.dumps({key: old_data[key] for key in changed_fields}) if old_data else None,
                new_data=json.dumps({key: new_data[key] for key in changed_fields}) if new_data else None
            )

    def save(self, *args, **kwargs):

        # refine fields
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to compress
                    print('\n\ncompressed')
                    compressed_image = self.compress_image(value)
                    setattr(self, field.name, compressed_image)
            elif isinstance(value, str):
                # Remove leading and trailing whitespaces
                value = value.strip()
                # Replace multiple spaces with a single space
                value = re.sub(r'\s+', ' ', value)
                setattr(self, field.name, value)

        # Fetch old data for logging
        old_data = None
        if not self._state.adding:
            old_data = type(self).objects.get(pk=self.pk).get_serializable_data()

        # Save the current instance
        super().save(*args, **kwargs)

        # Refetch the instance from the database to get new data
        new_data = self.get_serializable_data()

        # Log the changes
        self.log_change('Updated' if old_data else 'Created', old_data, new_data)


    def delete(self, *args, **kwargs):
        old_data = self.get_serializable_data()
        self.log_change('Deleted', old_data)
        super().delete(*args, **kwargs)





class DatabaseChangeLog(models.Model):
    model_name = models.CharField(max_length=255)
    change = models.CharField(max_length=255)  # 'Created', 'Updated', or 'Deleted'
    record_id = models.IntegerField()
    old_data = models.TextField(null=True, blank=True)  # Stores record data during update
    new_data = models.TextField(null=True, blank=True)  # Stores record data during update
    change_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.change_date.date()} - {self.model_name} - {self.change}'


class TuitionPlan(BaseModel):
    plan = models.CharField(max_length=255, default="")
    price = models.IntegerField()
    number_of_hours =  models.FloatField(null=True, blank=True)
    note = models.TextField(default="", blank=True, null=True)
    def __str__(self):
        return self.plan


class Discount(BaseModel):
    name = models.CharField(max_length=255, default="")
    discount_value = models.FloatField(default=0.0)
    def __str__(self):
        return self.name


class Attendance(BaseModel):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),    # Student is present
        ('absent', 'Absent'),      # Student is absent
        ('late', 'Late'),          # Student is late
        ('left_early', 'Left Early'),  # Student left early
    )

    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    check_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    check_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    learning_hours = models.FloatField(default=1.5, null=True, blank=True)

    is_paid_class = models.BooleanField(default=True) 
    note = models.TextField(default="", blank=True, null=True)
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} - {} - {} - {}".format(str(self.student), str(self.check_class), str(self.check_date), str(self.status))



class FinancialTransaction(BaseModel):
    IN_OR_OUT_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    TRANSACTION_TYPES = (
        ('income_tuition_fee', 'INCOME - Tuition Fee'),
        ('income_capital_contribution', 'INCOME - Capital Contribution'),
        ('income_product_sales', 'INCOME - Product Sales'),
        ('income_other_income', 'INCOME - Other Income'),
        ('expense_operational_expenses', 'EXPENSE - Operational Expenses'),
        ('expense_asset_expenditure', 'EXPENSE - Asset Expenditure'),
        ('expense_marketing_expenses', 'EXPENSE - Marketing Expenses'),
        ('expense_salary_expenses', 'EXPENSE - Salary Expenses'),
        ('expense_dividend_distribution', 'EXPENSE - Dividend Distribution'),
        ('expense_event_organization_expenses', 'EXPENSE - Event Organization Expenses'),
        ('expense_human_resources_expenses', 'EXPENSE - Human Resources Expenses'),
        ('expense_other_expenses', 'EXPENSE - Other Expenses'),
    )
    income_or_expense = models.CharField(max_length=20, choices=IN_OR_OUT_CHOICES)
    transaction_type = models.CharField(max_length=255, choices=TRANSACTION_TYPES)
    permission_giver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='given_transactions', blank=True)
    giver = models.CharField(max_length=100, default="Unspecified", null=True, blank=True)
    receiver = models.CharField(max_length=100, default="Unspecified", null=True, blank=True)
    amount = models.IntegerField(default=0, null=True, blank=True)

    # fields for tuition payments
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    tuition_plan = models.ForeignKey(TuitionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True)
    final_fee = models.IntegerField(default=0, null=True, blank=True)

    create_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(default="", blank=True, null=True)


    def save(self, *args, **kwargs):
        if self.student and self.tuition_plan:
            self.transaction_type = "income_tuition_fee"
            self.receiver = "GEN8 English School"
            self.giver = self.student.name

            percent = self.discount.discount_value
            self.final_fee = int(self.tuition_plan.price * (1 - percent))

            self.amount = int(self.final_fee)
            
        self.final_fee = int(self.final_fee)
        self.amount = int(self.amount)

        if self.transaction_type.startswith('income'):
            self.income_or_expense = 'income'
        else:
            self.income_or_expense = 'expense'

        return super().save(*args, **kwargs)

    def __str__(self):
        if self.student and self.tuition_plan:
            return f"{str(self.tuition_plan.plan)} - {str(self.student)} - {format_vnd(self.amount)} - {self.create_date}"
        else:
            return f"{str(self.transaction_type)} - {format_vnd(self.amount)} - {self.create_date}"


from django.utils.deconstruct import deconstructible
from uuid import uuid4
import os
@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]

        filename = 'transaction_{}_{}_{}.{}'.format(instance.financialtransaction.id, 
            datetime.now().strftime('%Y_%m_%d'), uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)

class TransactionImage(BaseModel):
    financialtransaction = models.ForeignKey(FinancialTransaction, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=PathAndRename('images/finance_images/'))


