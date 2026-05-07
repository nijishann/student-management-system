from rest_framework import serializers
from .models import Student, Parent, Teacher, Department, Subject


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
            'father_name', 'father_occupation', 'father_mobile', 'father_email',
            'mother_name', 'mother_occupation', 'mother_mobile', 'mother_email',
            'present_address', 'permanent_address'
        ]


class StudentSerializer(serializers.ModelSerializer):
    parent = ParentSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'first_name', 'last_name',
            'student_id', 'gender', 'date_of_birth',
            'student_class', 'section', 'religion',
            'mobile_number', 'admission_number',
            'joining_date', 'slug', 'parent'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name', 'first_name', 'last_name',
            'teacher_id', 'gender', 'date_of_birth',
            'mobile_number', 'email', 'joining_date',
            'qualification', 'slug',
            'department_name', 'subject_name'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'department_name', 'created_at']

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None