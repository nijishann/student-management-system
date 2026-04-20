from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from student.models import Student


@login_required
def index(request):
    total_students = Student.objects.count()
    recent_students = Student.objects.order_by('-id')[:5]
    unread_notification = request.user.notification_set.filter(is_read=False)
    unread_notification_count = unread_notification.count()
    context = {
        'total_students': total_students,
        'recent_students': recent_students,
        'unread_notification': unread_notification,
        'unread_notification_count': unread_notification_count,
    }
    return render(request, "Home/index.html", context)
