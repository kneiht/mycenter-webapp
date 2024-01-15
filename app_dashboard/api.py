from django.http import JsonResponse

from rest_framework import generics
from .models import FinancialTransaction
from rest_framework import serializers
from django.urls import reverse

# App-Specific Imports
from .models import (
    Class, Student, Attendance, Course, Discount, StudentClass,
    ClassSchedule, TuitionPlan, FinancialTransaction, DayTime, 
    User, TransactionImage, School
)

from django.db.models import Count, Sum  # 'Sum' is imported here

from rest_framework import viewsets






class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
    
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    from .models import ClassSchedule




class DayTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayTime
        fields = '__all__'
    
class DayTimeListCreateView(generics.ListCreateAPIView):
    queryset = DayTime.objects.all()
    serializer_class = DayTimeSerializer
    
class DaytimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DayTime.objects.all()
    serializer_class = DayTimeSerializer








class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = '__all__'
    
class ClassScheduleListCreateView(generics.ListCreateAPIView):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
    
class ClassScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer






class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'
    
class ClassListCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    
class ClassDetailViewz(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return JsonResponse({'status': 'error', 'message': str(exception)})


        # Current student ids in the class
        current_student_ids = set([str(student.id) for student in instance.students.all()])

        # Handling Many-to-Many relationship with Student
        if 'selected_students' in request.data:
            
            # Get data students from form
            new_student_ids = set(request.data.getlist('selected_students'))


            # Find students to add and students to remove
            students_to_add = new_student_ids - current_student_ids
            students_to_remove = current_student_ids - new_student_ids

            # Remove students that are no longer in the class
            for student_id in students_to_remove:
                student = Student.objects.get(id=student_id)
                instance.students.remove(student)

            # Add new students to the class
            for student_id in students_to_add:
                student = Student.objects.get(id=student_id)
                instance.students.add(student)
        else:
            # Remove all students
            for student_id in current_student_ids:
                student = Student.objects.get(id=student_id)
                instance.students.remove(student)


        self.perform_update(serializer)

        if 'selected_students' in request.data:
            new_paid_class_student_ids = set(request.data.getlist('paid_class_students'))
            class_students = StudentClass.objects.filter(_class=instance)
            for class_student in class_students:
                if str(class_student.student.id) in new_paid_class_student_ids:
                    class_student.is_paid_class = True
                else:
                    class_student.is_paid_class = False
                class_student.save()


        return JsonResponse({'status': 'success', 'message': 'Updated successfully'})

    def perform_update(self, serializer):
        serializer.save()





class StudentSerializer(serializers.ModelSerializer):
    #total_paid_hours = serializers.SerializerMethodField()
    #total_paid_hours_used = serializers.SerializerMethodField()
    #total_paid_hours_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    '''
    def get_total_paid_hours_used(self, obj):
        sum_paid_class_hours = Attendance.objects.filter(student=obj, is_paid_class=True).aggregate(Sum('learning_hours'))
        # The aggregate function returns a dictionary, so you need to extract the value
        return sum_paid_class_hours['learning_hours__sum'] or 0  # Returns 0 if the result is None

    def get_total_paid_hours_remaining(self, obj):
        # Calculate Total Paid Lessons for each student
        total_paid_hours = FinancialTransaction.objects.filter(student=obj).aggregate(total=Sum('tuition_plan__number_of_hours'))['total'] or 0
        total_paid_hours_used = Attendance.objects.filter(student=obj, is_paid_class=True).aggregate(Sum('learning_hours'))
        total_paid_hours_used = total_paid_hours_used['learning_hours__sum'] or 0  # Returns 0 if the result is None
        return total_paid_hours - total_paid_hours_used
    '''

    
class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all().order_by('id')
    serializer_class = StudentSerializer
    
class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            print(exception)
            return JsonResponse({'status': 'error', 'message': str(exception)})

        # Current class ids in the class
        current_class_ids = set([str(_class.id) for _class in instance.classes.all()])


        # Handling Many-to-Many relationship with Class
        if 'selected_classes' in request.data:
            
            # Get data classes from form
            new_class_ids = set(request.data.getlist('selected_classes'))

            # Find classes to add and classes to remove
            classes_to_add = new_class_ids - current_class_ids
            classes_to_remove = current_class_ids - new_class_ids

            # Remove classes that are no longer in the student
            for class_id in classes_to_remove:
                _class = Class.objects.get(id=class_id)
                instance.classes.remove(_class)

            # Add new students to the class
            for class_id in classes_to_add:
                _class = Class.objects.get(id=class_id)
                instance.classes.add(_class)
        else:
            # Remove classes that are no longer in the student
            for class_id in current_class_ids:
                _class = Class.objects.get(id=class_id)
                instance.classes.remove(_class)

        self.perform_update(serializer)

        if 'selected_classes' in request.data:
            new_paid_classes_ids = set(request.data.getlist('paid_classes'))
            student_classes = StudentClass.objects.filter(student=instance)
            for student_class in student_classes:
                if str(student_class._class.id) in new_paid_classes_ids:
                    student_class.is_paid_class = True
                else:
                    student_class.is_paid_class = False
                student_class.save()


        return JsonResponse({'status': 'success', 'message': 'Updated successfully'})

    def perform_update(self, serializer):
        serializer.save()



class TuitionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuitionPlan
        fields = '__all__'
    
class TuitionPlanListCreateView(generics.ListCreateAPIView):
    queryset = TuitionPlan.objects.all()
    serializer_class = TuitionPlanSerializer
    
class TuitionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TuitionPlan.objects.all()
    serializer_class = TuitionPlanSerializer




class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
    
class DiscountListCreateView(generics.ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    
class DiscountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer





class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
    
class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    
class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    



class FinancialTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialTransaction
        fields = '__all__'


from rest_framework.response import Response
from rest_framework import status
class FinancialTransactionListCreateView(generics.ListCreateAPIView):
    queryset = FinancialTransaction.objects.all()
    serializer_class = FinancialTransactionSerializer
    
    def create(self, request, *args, **kwargs):
        # Check if 'student' and 'tuition_plan' are present in the request data
        student_id = request.data.get('student')
        tuition_plan_id = request.data.get('tuition_plan')
        
        # Create a mutable copy of request.data
        mutable_data = request.data.copy()
        
        # Set default values for 'income_or_expense' and 'transaction_type'
        if student_id and tuition_plan_id:
            mutable_data['income_or_expense'] = 'income'
            mutable_data['transaction_type'] = 'income_tuition_fee'
        
        serializer = self.get_serializer(data=mutable_data)
        if serializer.is_valid():
            financial_transaction = serializer.save()

            # Process and save the image files
            images = request.FILES.getlist('images')  # Make sure 'images' matches the key in your FormData
            for image_file in images:
                TransactionImage.objects.create(
                    financialtransaction=financial_transaction,  # Link to the created transaction
                    image=image_file
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class FinancialTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FinancialTransaction.objects.all()
    serializer_class = FinancialTransactionSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)

            # Process and save new image files if present
            images = request.FILES.getlist('images')
            for image_file in images:
                TransactionImage.objects.create(
                    financialtransaction=instance,
                    image=image_file
                )   

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()


