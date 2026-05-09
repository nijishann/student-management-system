from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Teacher, Department, Subject
from .serializers import (
    StudentSerializer, TeacherSerializer,
    DepartmentSerializer, SubjectSerializer
)


# ========== STUDENT API ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list_api(request):
    """List of all students"""
    students = Student.objects.select_related('parent').all()

    # Search filter
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            first_name__icontains=search
        ) | students.filter(
            last_name__icontains=search
        ) | students.filter(
            student_id__icontains=search
        )

    # Class filter
    student_class = request.GET.get('class', '')
    if student_class:
        students = students.filter(student_class=student_class)

    serializer = StudentSerializer(students, many=True)
    return Response({
        'count': students.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_detail_api(request, pk):
    """Details of a student"""
    try:
        student = Student.objects.select_related('parent').get(pk=pk)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = StudentSerializer(student)
    return Response(serializer.data)


# ========== TEACHER API ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_list_api(request):
    """List of all teachers"""
    teachers = Teacher.objects.select_related('department', 'subject').all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response({
        'count': teachers.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_detail_api(request, pk):
    """Details of a teacher"""
    try:
        teacher = Teacher.objects.get(pk=pk)
    except Teacher.DoesNotExist:
        return Response(
            {'error': 'Teacher not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TeacherSerializer(teacher)
    return Response(serializer.data)


# ========== DEPARTMENT API ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_list_api(request):
    """List of all departments"""
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response({
        'count': departments.count(),
        'results': serializer.data
    })


# ========== SUBJECT API ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subject_list_api(request):
    """List of all subjects"""
    subjects = Subject.objects.select_related('department').all()
    serializer = SubjectSerializer(subjects, many=True)
    return Response({
        'count': subjects.count(),
        'results': serializer.data
    })


# ========== SUMMARY API ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_summary(request):
    """Count of all records"""
    return Response({
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_departments': Department.objects.count(),
        'total_subjects': Subject.objects.count(),
    })