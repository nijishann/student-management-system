from django.urls import path
from . import views
from . import api_views

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

    # Registration 
    path('register/', views.register_page, name='register_page'),
    path('register/submit/', views.register_submit, name='register_submit'),

    # Realtime Username Check 
    path('check-username/', views.check_username, name='check_username'),

    # Email Verification 
    path('send-email-otp/', views.send_email_otp, name='send_email_otp'),
    path('verify-email-otp/', views.verify_email_otp, name='verify_email_otp'),

    # Phone Verification 
    path('send-phone-otp/', views.send_phone_otp, name='send_phone_otp'),
    path('verify-phone-otp/', views.verify_phone_otp, name='verify_phone_otp'),

    # Login Realtime Check — নতুন
    path('check-login-username/', views.check_login_username, name='check_login_username'),
    path('check-login-password/', views.check_login_password, name='check_login_password'),

    # Forget Password — নতুন
    path('forget-password/', views.forget_password, name='forget_password'),
    path('send-reset-otp/', views.send_reset_otp, name='send_reset_otp'),
    path('verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Rating — নতুন
    path('view/<slug:slug>/rate/', views.rate_student, name='rate_student'),

    # REST API
    path('api/summary/', api_views.api_summary, name='api_summary'),
    path('api/students/', api_views.student_list_api, name='student_list_api'),
    path('api/students/<int:pk>/', api_views.student_detail_api, name='student_detail_api'),
    path('api/teachers/', api_views.teacher_list_api, name='teacher_list_api'),
    path('api/teachers/<int:pk>/', api_views.teacher_detail_api, name='teacher_detail_api'),
    path('api/departments/', api_views.department_list_api, name='department_list_api'),
    path('api/subjects/', api_views.subject_list_api, name='subject_list_api'),
    
    # AI Prediction
    path('predict/<slug:slug>/', views.predict_student, name='predict_student'),
]