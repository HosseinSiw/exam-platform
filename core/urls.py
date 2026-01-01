from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('home.urls'), name='home'),
    path('users/', include('users.urls'), name='users'),
    path('courses/', include('courses.urls'), name='courses'),
    path('exam/', include('exams.urls'), name='exams'),
    path('results/', include('results.urls'), name='results'),
]
