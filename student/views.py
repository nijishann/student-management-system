from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Student, Parent, Teacher, Department, Subject, Comment, Like, StudentRegistration, Rating,StudentResult
from django.contrib import messages
from .utilis import create_notification
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
import json
import random
from django.contrib.auth.models import User
from django.contrib.auth import login
from .ml_model import predict_result

def get_notifications(request):
    unread_notification = request.user.notification_set.filter(is_read=False)
    return {
        'unread_notification': unread_notification,
        'unread_notification_count': unread_notification.count(),
    }


def make_unique_slug(first_name, last_name, student_id, instance_id=None):
    base_slug = slugify(f"{first_name}-{last_name}-{student_id}")
    slug = base_slug
    qs = Student.objects.filter(slug=slug)
    if instance_id:
        qs = qs.exclude(pk=instance_id)
    if qs.exists():
        slug = f"{base_slug}-{instance_id or 1}"
    return slug


@login_required
def add_student(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        student_class = ""
        religion = request.POST.get('religion')
        joining_date = request.POST.get('joining_date')
        mobile_number = request.POST.get('mobile_number')
        admission_number = request.POST.get('admission_number')
        section = request.POST.get('section')
        student_image = request.FILES.get('student_image')

        father_name = request.POST.get('father_name')
        father_occupation = request.POST.get('father_occupation')
        father_mobile = request.POST.get('father_mobile')
        father_email = request.POST.get('father_email')
        mother_name = request.POST.get('mother_name')
        mother_occupation = request.POST.get('mother_occupation')
        mother_mobile = request.POST.get('mother_mobile')
        mother_email = request.POST.get('mother_email')
        present_address = request.POST.get('present_address')
        permanent_address = request.POST.get('permanent_address')

        parent = Parent.objects.create(
            father_name=father_name,
            father_occupation=father_occupation,
            father_mobile=father_mobile,
            father_email=father_email,
            mother_name=mother_name,
            mother_occupation=mother_occupation,
            mother_mobile=mother_mobile,
            mother_email=mother_email,
            present_address=present_address,
            permanent_address=permanent_address
        )

        slug = slugify(f"{first_name}-{last_name}-{student_id}")
        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            gender=gender,
            date_of_birth=date_of_birth,
            student_class=student_class,
            religion=religion,
            joining_date=joining_date,
            mobile_number=mobile_number,
            admission_number=admission_number,
            section=section,
            student_image=student_image,
            parent=parent,
            slug=slug
        )
        create_notification(request.user, f"Added Student: {student.first_name} {student.last_name}")
        messages.success(request, "Student added successfully!")
        return redirect('student_list')

    context = get_notifications(request)
    return render(request, "students/add-student.html", context)


from django.core.paginator import Paginator

@login_required
def student_list(request):
    students_all = Student.objects.select_related('parent').all()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        students_all = students_all.filter(
            first_name__icontains=search
        ) | students_all.filter(
            last_name__icontains=search
        ) | students_all.filter(
            student_id__icontains=search
        )

    # Pagination - 5 per page
    paginator = Paginator(students_all, 5)
    page_number = request.GET.get('page')
    student_list = paginator.get_page(page_number)

    context = {
        'student_list': student_list,
        'search': search,
        **get_notifications(request),
    }
    return render(request, "students/students.html", context)


@login_required
def edit_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    parent = student.parent

    if request.method == "POST":
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.student_id = request.POST.get('student_id')
        student.gender = request.POST.get('gender')
        student.date_of_birth = request.POST.get('date_of_birth')
        student.student_class = request.POST.get('student_class')
        student.religion = request.POST.get('religion')
        student.joining_date = request.POST.get('joining_date')
        student.mobile_number = request.POST.get('mobile_number')
        student.admission_number = request.POST.get('admission_number')
        student.section = request.POST.get('section')
        if request.FILES.get('student_image'):
            student.student_image = request.FILES.get('student_image')
        student.slug = slugify(f"{student.first_name}-{student.last_name}-{student.student_id}")
        student.save()

        parent.father_name = request.POST.get('father_name')
        parent.father_occupation = request.POST.get('father_occupation')
        parent.father_mobile = request.POST.get('father_mobile')
        parent.father_email = request.POST.get('father_email')
        parent.mother_name = request.POST.get('mother_name')
        parent.mother_occupation = request.POST.get('mother_occupation')
        parent.mother_mobile = request.POST.get('mother_mobile')
        parent.mother_email = request.POST.get('mother_email')
        parent.present_address = request.POST.get('present_address')
        parent.permanent_address = request.POST.get('permanent_address')
        parent.save()

        create_notification(request.user, f"Updated Student: {student.first_name} {student.last_name}")
        messages.success(request, "Student updated successfully!")
        return redirect('student_list')

    context = {
        'student': student,
        'parent': parent,
        **get_notifications(request),
    }
    return render(request, "students/edit-student.html", context)


@login_required
def view_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    comments = student.comments.select_related('user').order_by('-created_at')
    like_count = student.likes.filter(is_like=True).count()
    dislike_count = student.likes.filter(is_like=False).count()
    user_reaction = student.likes.filter(user=request.user).first()

    # Rating
    ratings = student.ratings.all()
    total_ratings = ratings.count()
    avg_rating = round(sum(r.score for r in ratings) / total_ratings, 1) if total_ratings > 0 else 0
    user_rating = ratings.filter(user=request.user).first()

    context = {
        'student': student,
        'comments': comments,
        'like_count': like_count,
        'dislike_count': dislike_count,
        'user_reaction': user_reaction,
        'avg_rating': avg_rating,
        'total_ratings': total_ratings,
        'user_rating': user_rating.score if user_rating else 0,
        **get_notifications(request),
    }
    return render(request, "students/student-details.html", context)

@login_required
@require_POST
def add_comment(request, slug):
    student = get_object_or_404(Student, slug=slug)
    data = json.loads(request.body)
    text = data.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Empty comment'}, status=400)
    comment = Comment.objects.create(
        student=student,
        user=request.user,
        text=text
    )
    return JsonResponse({
        'id': comment.id,
        'username': comment.user.username,
        'text': comment.text,
        'created_at': comment.created_at.strftime("%d %b %Y, %I:%M %p")
    })


@login_required
@require_POST
def toggle_like(request, slug):
    student = get_object_or_404(Student, slug=slug)
    data = json.loads(request.body)
    is_like = data.get('is_like')  # True or False

    existing = Like.objects.filter(student=student, user=request.user).first()

    if existing:
        if existing.is_like == is_like:
            # Clicking same button again will remove reaction
            existing.delete()
        else:
            # Clicking other button will switch reaction
            existing.is_like = is_like
            existing.save()
    else:
        Like.objects.create(student=student, user=request.user, is_like=is_like)

    like_count = student.likes.filter(is_like=True).count()
    dislike_count = student.likes.filter(is_like=False).count()

    return JsonResponse({
        'like_count': like_count,
        'dislike_count': dislike_count,
    })



@login_required
def delete_student(request, slug):
    if request.method == "POST":
        student = get_object_or_404(Student, slug=slug)
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()
        create_notification(request.user, f"Deleted student: {student_name}")
        messages.success(request, f"Student '{student_name}' deleted successfully!")
        return redirect('student_list')
    return HttpResponseForbidden()

# ===================== TEACHER VIEWS =====================

@login_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('department', 'subject').all()
    context = {
        'teacher_list': teachers,
        **get_notifications(request),
    }
    return render(request, "teachers/teacher-list.html", context)


@login_required
def add_teacher(request):
    departments = Department.objects.all()
    subjects = Subject.objects.all()
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        teacher_id = request.POST.get('teacher_id')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        joining_date = request.POST.get('joining_date')
        qualification = request.POST.get('qualification')
        department_id = request.POST.get('department')
        subject_id = request.POST.get('subject')
        teacher_image = request.FILES.get('teacher_image')

        base_slug = slugify(f"{first_name}-{last_name}-{teacher_id}")
        slug = base_slug
        counter = 1
        while Teacher.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        Teacher.objects.create(
            first_name=first_name,
            last_name=last_name,
            teacher_id=teacher_id,
            gender=gender,
            date_of_birth=date_of_birth,
            mobile_number=mobile_number,
            email=email,
            joining_date=joining_date,
            qualification=qualification,
            department_id=department_id if department_id else None,
            subject_id=subject_id if subject_id else None,
            teacher_image=teacher_image,
            slug=slug
        )
        create_notification(request.user, f"Added Teacher: {first_name} {last_name}")
        messages.success(request, "Teacher added successfully!")
        return redirect('teacher_list')

    context = {
        'departments': departments,
        'subjects': subjects,
        **get_notifications(request),
    }
    return render(request, "teachers/add-teacher.html", context)


@login_required
def view_teacher(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)
    context = {
        'teacher': teacher,
        **get_notifications(request),
    }
    return render(request, "teachers/teacher-details.html", context)


# ===================== DEPARTMENT VIEWS =====================

@login_required
def department_list(request):
    departments = Department.objects.all()
    context = {
        'department_list': departments,
        **get_notifications(request),
    }
    return render(request, "departments/department-list.html", context)


@login_required
def add_department(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        Department.objects.create(name=name, description=description)
        create_notification(request.user, f"Added Department: {name}")
        messages.success(request, "Department added successfully!")
        return redirect('department_list')
    context = get_notifications(request)
    return render(request, "departments/add-department.html", context)


# ===================== SUBJECT VIEWS =====================

@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('department').all()
    context = {
        'subject_list': subjects,
        **get_notifications(request),
    }
    return render(request, "subjects/subject-list.html", context)


@login_required
def add_subject(request):
    departments = Department.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        department_id = request.POST.get('department')
        Subject.objects.create(
            name=name,
            description=description,
            department_id=department_id if department_id else None
        )
        create_notification(request.user, f"Added Subject: {name}")
        messages.success(request, "Subject added successfully!")
        return redirect('subject_list')
    context = {
        'departments': departments,
        **get_notifications(request),
    }
    return render(request, "subjects/add-subject.html", context)


# ========== REGISTRATION PAGE ==========

def register_page(request):
    return render(request, "registration/register.html")


# ========== REALTIME USERNAME CHECK ==========

def check_username(request):
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'available': False, 'message': 'Please enter a username'})
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': '❌ Minimum 3 characters required'})

    # Check in Django User table
    exists = User.objects.filter(username=username).exists()
    if exists:
        return JsonResponse({'available': False, 'message': '❌ This username is already taken'})
    return JsonResponse({'available': True, 'message': '✅ This username is available'})


# ========== EMAIL OTP SEND ==========

def send_email_otp(request):
    email = request.GET.get('email', '').strip()
    if not email:
        return JsonResponse({'success': False, 'message': 'Email here'})

    if StudentRegistration.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': '❌ This email is already registered'})

    otp = str(random.randint(100000, 999999))
    request.session['email_otp'] = otp
    request.session['email_to_verify'] = email

    try:
        send_mail(
            subject='Email Verification OTP',
            message=f'OTP: {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({
            'success': True,
            'message': f'✅ OTP Sent',
            'dev_otp': otp  # Email OTP will also show on screen
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'❌ Error: {str(e)}'  # Error টা দেখাবে
        })


# ========== EMAIL OTP VERIFY ==========

def verify_email_otp(request):
    otp_input = request.GET.get('otp', '').strip()
    saved_otp = request.session.get('email_otp', '')
    if not saved_otp:
        return JsonResponse({'success': False, 'message': 'First OTP Send'})
    if otp_input == saved_otp:
        request.session['email_verified'] = True
        return JsonResponse({'success': True, 'message': '✅ Email verified!'})
    return JsonResponse({'success': False, 'message': '❌ Incorrect OTP'})


# ========== PHONE OTP SEND (Simulated) ==========

def send_phone_otp(request):
    phone = request.GET.get('phone', '').strip()
    if not phone:
        return JsonResponse({'success': False, 'message': 'Phone number'})
    if len(phone) < 11:
        return JsonResponse({'success': False, 'message': '❌ Please enter a valid phone number'})

    # Phone already exists check
    if StudentRegistration.objects.filter(phone=phone).exists():
        return JsonResponse({'success': False, 'message': '❌ Already registered'})

    # OTP generated (simulated — real SMS gateway needed for production)
    otp = str(random.randint(100000, 999999))
    request.session['phone_otp'] = otp
    request.session['phone_to_verify'] = phone

    # OTP will be shown in response during development
    return JsonResponse({
        'success': True,
        'message': f'✅ OTP Sent,(Demo: {otp})',
        'dev_otp': otp  # Remove this line in production
    })


# ========== PHONE OTP VERIFY ==========

def verify_phone_otp(request):
    otp_input = request.GET.get('otp', '').strip()
    saved_otp = request.session.get('phone_otp', '')
    if not saved_otp:
        return JsonResponse({'success': False, 'message': 'First OTP Send'})
    if otp_input == saved_otp:
        request.session['phone_verified'] = True
        return JsonResponse({'success': True, 'message': '✅ Phone verified!'})
    return JsonResponse({'success': False, 'message': '❌ Incorrect OTP'})


# ========== FINAL REGISTRATION SUBMIT ==========

def register_submit(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Verification check
        if not request.session.get('email_verified'):
            messages.error(request, '❌ Please verify your email!')
            return redirect('register_page')
        if not request.session.get('phone_verified'):
            messages.error(request, '❌ Please verify your phone!')
            return redirect('register_page')

        # Username already exists check
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ This username is already taken!')
            return redirect('register_page')

        # Email already exists check
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ This email is already registered!')
            return redirect('register_page')

        # Create Django User
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Also save to StudentRegistration
        StudentRegistration.objects.create(
            username=username,
            email=email,
            phone=phone,
            password=password,
            is_email_verified=True,
            is_phone_verified=True,
        )

        # Session clear
        for key in ['email_otp', 'phone_otp', 'email_verified', 'phone_verified']:
            request.session.pop(key, None)

        # Redirect to success page
        return render(request, 'registration/success.html', {
            'username': username,
            'email': email,
            'phone': phone,
        })

    return redirect('register_page')


# ========== REALTIME LOGIN USERNAME CHECK ==========
def check_login_username(request):
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'exists': False, 'message': ''})
    
    exists = User.objects.filter(username=username).exists()
    if exists:
        return JsonResponse({'exists': True, 'message': '✅ Username found'})
    return JsonResponse({'exists': False, 'message': '❌ This username is not registered'})


# ========== REALTIME LOGIN PASSWORD CHECK ==========
def check_login_password(request):
    username = request.GET.get('username', '').strip()
    password = request.GET.get('password', '').strip()
    
    if not username or not password:
        return JsonResponse({'correct': False, 'message': ''})
    
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    if user is not None:
        return JsonResponse({'correct': True, 'message': '✅ Password is correct'})
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({'correct': False, 'message': '❌ Incorrect password!'})
    return JsonResponse({'correct': False, 'message': '❌ Please enter a valid username first'})

# ========== FORGET PASSWORD ==========

def forget_password(request):
    return render(request, 'registration/forget-password.html')


def send_reset_otp(request):
    email = request.GET.get('email', '').strip()
    if not email:
        return JsonResponse({'success': False, 'message': '❌ Please enter your email'})

    # Check if email is registered
    user = User.objects.filter(email=email).first()
    if not user:
        return JsonResponse({'success': False, 'message': '❌ No account found with this email'})

    # OTP generate
    otp = str(random.randint(100000, 999999))
    request.session['reset_otp'] = otp
    request.session['reset_email'] = email

    # Send email
    try:
        send_mail(
            subject='Password Reset OTP - Student Management System',
            message=f'Your Password Reset OTP: {otp}\n\nThis code is valid for 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({
            'success': True,
            'message': f'✅ OTP has been sent to {email} তে',
            'dev_otp': otp  # Development এ দেখাবে
        })
    except Exception as e:
        return JsonResponse({
            'success': True,
            'message': f'✅ OTP has been sent to (Demo)',
            'dev_otp': otp
        })


def verify_reset_otp(request):
    otp_input = request.GET.get('otp', '').strip()
    saved_otp = request.session.get('reset_otp', '')

    if not saved_otp:
        return JsonResponse({'success': False, 'message': '❌ Please send OTP first'})
    if otp_input == saved_otp:
        request.session['reset_verified'] = True
        return JsonResponse({'success': True, 'message': '✅ OTP verified! Please enter new password'})
    return JsonResponse({'success': False, 'message': '❌ Incorrect OTP'})


def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Verification check
        if not request.session.get('reset_verified'):
            messages.error(request, '❌ Please verify OTP first!')
            return redirect('forget_password')

        # Password match check
        if new_password != confirm_password:
            messages.error(request, '❌ Passwords do not match!')
            return redirect('forget_password')

        # Password length check
        if len(new_password) < 6:
            messages.error(request, '❌ Password must be at least 6 characters!')
            return redirect('forget_password')

        # Update password
        email = request.session.get('reset_email')
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()

            # Session clear
            for key in ['reset_otp', 'reset_email', 'reset_verified']:
                request.session.pop(key, None)

            messages.success(request, '✅ Password changed successfully! Please login.')
            return redirect('login')

        messages.error(request, '❌ User not found!')
        return redirect('forget_password')

    return redirect('forget_password')

# ========== RATING ==========
@login_required
@require_POST
def rate_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    data = json.loads(request.body)
    score = int(data.get('score', 0))

    if score < 1 or score > 5:
        return JsonResponse({'error': 'Invalid score'}, status=400)

    rating, created = Rating.objects.update_or_create(
        student=student,
        user=request.user,
        defaults={'score': score}
    )

    ratings = student.ratings.all()
    total_ratings = ratings.count()
    avg_rating = round(sum(r.score for r in ratings) / total_ratings, 1) if total_ratings > 0 else 0

    return JsonResponse({
        'avg_rating': avg_rating,
        'total_ratings': total_ratings,
        'user_score': score,
    })

# ========== AI PREDICTION ==========

@login_required
def predict_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    prediction_result = None
    previous_results = StudentResult.objects.filter(student=student).order_by('-id')[:5]

    if request.method == "POST":
        attendance = float(request.POST.get('attendance', 0))
        math = float(request.POST.get('math_marks', 0))
        english = float(request.POST.get('english_marks', 0))
        science = float(request.POST.get('science_marks', 0))
        bangla = float(request.POST.get('bangla_marks', 0))

        # Run prediction
        prediction_result = predict_result(attendance, math, english, science, bangla)

        # Save to database
        StudentResult.objects.create(
            student=student,
            attendance=attendance,
            math_marks=math,
            english_marks=english,
            science_marks=science,
            bangla_marks=bangla,
            prediction=prediction_result['prediction'],
            confidence=prediction_result['confidence']
        )

        create_notification(
            request.user,
            f"AI Prediction for {student.first_name}: {prediction_result['prediction']}"
        )

    context = {
        'student': student,
        'prediction_result': prediction_result,
        'previous_results': previous_results,
        **get_notifications(request),
    }
    return render(request, 'students/predict.html', context)