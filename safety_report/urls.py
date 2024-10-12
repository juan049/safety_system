from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Home
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    #registrar proyecto
    path('project_register', views.project_register, name='project_register'),
    #Inicar auditoria de seguridad
    path('project_findings/<int:project_id>/audit', views.project_findings_audit, name='project_findings_audit'),
    #REgistrar finding
    path('project_findings/<int:project_id>/register/<int:finding_classification_id>', views.project_findings_register, name='project_findings_register'),
    #Mostrar los findings del proyecto
    path('project_findings/<int:project_id>', views.project_findings, name='project_findings'),
    
    #Subir foto de corrección
    path('project_findings/<int:finding_id>/upload_correction_image', views.project_findings_upload_correction_image, name='project_findings_upload_correction_image'),
    
    
    
    #Ver reporte
    path('project_findings_report', views.project_findings_report, name='project_findings_report'),
    #Descargar Reporte
     path('project_findings_report_download', views.project_findings_report_download, name='project_findings_report_download')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)