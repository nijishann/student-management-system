from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 
from django.conf import settings 
from django.conf.urls.static import static 
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('', include("school.urls")),
    path('student/', include("student.urls")),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






