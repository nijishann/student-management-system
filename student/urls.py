from django.urls import path
from . import views

urlpatterns = [
    # Student
    path("", views.student_list, name='student_list'),
    path("add/", views.add_student, name="add_student"),
    path('view/<slug:slug>/', views.view_student, name="view_student"),
    path('edit/<slug:slug>/', views.edit_student, name='edit_student'),
    path('delete/<slug:slug>/', views.delete_student, name='delete_student'),

    # Comment & Like 
    path('view/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('view/<slug:slug>/like/', views.toggle_like, name='toggle_like'),


    # Teacher
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/view/<slug:slug>/', views.view_teacher, name='view_teacher'),

    # Department
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),

    # Subject
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
]