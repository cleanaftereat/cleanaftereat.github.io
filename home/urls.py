from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('student_info/', views.student_info, name='student_info'),
    path('calculator/', views.calculator, name='calculator'),
    path('info_check/', views.info_check, name='info_check'),
    path('academic_status/', views.academic_status, name='academic_status'),
    path('about/', views.about, name='about',)
]
