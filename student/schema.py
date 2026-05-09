import graphene
from graphene_django import DjangoObjectType
from .models import Student, Teacher, Department, Subject


# ========== TYPES ==========

class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        fields = (
            'id', 'first_name', 'last_name', 'student_id',
            'gender', 'student_class', 'section', 'religion',
            'mobile_number', 'admission_number', 'joining_date',
            'date_of_birth', 'slug'
        )


class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = (
            'id', 'first_name', 'last_name', 'teacher_id',
            'gender', 'mobile_number', 'email',
            'joining_date', 'qualification', 'slug'
        )


class DepartmentType(DjangoObjectType):
    class Meta:
        model = Department
        fields = ('id', 'name', 'description', 'created_at')


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description', 'created_at')


# ========== QUERIES ==========

class Query(graphene.ObjectType):

    # All students
    all_students = graphene.List(StudentType)

    # Single student by slug
    student = graphene.Field(StudentType, slug=graphene.String())

    # Search students by class
    students_by_class = graphene.List(
        StudentType,
        student_class=graphene.String()
    )

    # All teachers
    all_teachers = graphene.List(TeacherType)

    # All departments
    all_departments = graphene.List(DepartmentType)

    # All subjects
    all_subjects = graphene.List(SubjectType)

    # Total count
    student_count = graphene.Int()
    teacher_count = graphene.Int()

    # Resolvers
    def resolve_all_students(self, info):
        return Student.objects.select_related('parent').all()

    def resolve_student(self, info, slug):
        try:
            return Student.objects.get(slug=slug)
        except Student.DoesNotExist:
            return None

    def resolve_students_by_class(self, info, student_class):
        return Student.objects.filter(student_class=student_class)

    def resolve_all_teachers(self, info):
        return Teacher.objects.all()

    def resolve_all_departments(self, info):
        return Department.objects.all()

    def resolve_all_subjects(self, info):
        return Subject.objects.all()

    def resolve_student_count(self, info):
        return Student.objects.count()

    def resolve_teacher_count(self, info):
        return Teacher.objects.count()


schema = graphene.Schema(query=Query)