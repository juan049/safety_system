from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('project_findings/<int:id>', views.project_findings, name='project_findings'),
    path('project_findings/<int:id>/register', views.project_findings_register, name='project_findings_register'),
    path('project_findings_report', views.project_findings_report, name='project_findings_report')
]