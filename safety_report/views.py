import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

from django.http import JsonResponse
from django.db.models import Max
from django.http import HttpResponseForbidden


from .forms import ProjectRegisterForm, FindingRegisterForm

from xhtml2pdf import pisa
import base64

from datetime import datetime, timedelta


from .models import Project, Finding, FindingClassification, Contractor, Image, ProjectContractor, Comment, ProjectUser

# Create your views here.

def home(request):
    projects = list(Project.objects.all())
    return render(request, 'home.html', {
        "projects": projects
    })
#Listado de proyectos
def projects(request):
    # Si el usuario es staff o superuser, puede ver todos los proyectos
    if request.user.is_staff or request.user.is_superuser:
        projects = Project.objects.all().annotate(last_finding_date=Max('finding__created_at'))
    else:
        # Si no es staff ni superuser, solo puede ver los proyectos en los que está registrado en ProjectUser
        projects = Project.objects.filter(projectuser__user=request.user).annotate(last_finding_date=Max('finding__created_at'))
    return render(request, 'projects.html', {"projects": projects})

#Crear proyecto
def project_register(request):
    if request.method == 'POST':
        form = ProjectRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # Verificar si el archivo PDF fue cargado
            if 'pdf_plan' in request.FILES:
                print("PDF cargado correctamente")
            else:
                print("No se ha cargado ningún PDF")

            project = form.save()
            return redirect('project_findings', project_id=project.id)
    else:
        form = ProjectRegisterForm()
    return render(request, 'project_register.html', {'form': form})

def project_findings_audit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    finding_classifications = FindingClassification.objects.all()
    return render(request, 'project_findings_audit.html', {
        "project": project,
        "finding_classifications": finding_classifications
    })
    
def project_findings_register(request, project_id, finding_classification_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        
        finding_register_form = FindingRegisterForm(request.POST, request.FILES, project_id=project_id, finding_classification_id=finding_classification_id)

        # Obtener la imagen del canvas desde el campo oculto
        image_data = request.POST.get('image_data')  # Asumiendo que el campo oculto se llama 'image_data'
        print(request.POST)
        # Obtener las coordenadas desde el request
        pin_x = request.POST.get('pin_x')  # Cambia 'pin_x' al nombre del campo correcto en tu formulario
        pin_y = request.POST.get('pin_y')  # Cambia 'pin_y' al nombre del campo correcto en tu formulario

        # Imprimir las coordenadas para depuración
        print(f"Coordenadas recibidas: pin_x={pin_x}, pin_y={pin_y}")

        if finding_register_form.is_valid():
            finding = finding_register_form.save(commit=False)
            finding.project_id = project_id  # Asignar el project_id aquí
            finding.author = request.user

            # Asignar las coordenadas
            finding.pin_x = pin_x
            finding.pin_y = pin_y
            print(f'Coordenadas recibidas: pin_x={request.POST.get("pin_x")}, pin_y={request.POST.get("pin_y")}')
            # Guardar la imagen del canvas si se proporciona
            if image_data:
                finding.before_image.save(finding.title + '.png', ContentFile(base64.b64decode(image_data.split(',')[1])), save=False)

            finding.save()
            # Redirigir o mostrar mensaje de éxito
            return redirect('project_findings_audit', project_id=project_id)
    else:
        finding_register_form = FindingRegisterForm(project_id=project_id, finding_classification_id=finding_classification_id)

    return render(request, 'project_findings_register.html', {
        'project': project,
        'finding_register_form': finding_register_form,
    })


def project_findings(request, project_id):
    if not (request.user.is_staff or request.user.is_superuser or ProjectUser.objects.filter(user=request.user, project_id=project_id).exists()):
        return HttpResponseForbidden("No tienes permiso para acceder a este proyecto.")
    project = get_object_or_404(Project, id=project_id)
    
    # Obtiene los hallazgos ordenados por fecha de creación de forma descendente
    findings = Finding.objects.filter(project_id=project_id).order_by('-created_at')
    
    # Paginación: muestra 15 hallazgos por página
    paginator = Paginator(findings, 15)  # 15 hallazgos por página
    page_number = request.GET.get('page')
    findings_page = paginator.get_page(page_number)

    # Aquí puedes agregar lógica adicional para estadísticas, si lo deseas
    total_findings = findings.count()
    
    return render(request, 'project_findings.html', {
        "project": project,
        "findings": findings_page,
        "total_findings": total_findings  # Pasar total de hallazgos al contexto
    })

    
def project_findings_upload_correction_image(request, finding_id):
    finding = get_object_or_404(Finding, id=finding_id)

    if request.method == 'POST' and request.FILES.get('after_image'):
        # Guarda la imagen subida en el campo after_image
        finding.after_image = request.FILES['after_image']
        finding.save()
        print('Imagen de corrección subida exitosamente.')
        return redirect('project_findings', finding.project.id )
    else:
        print('Error al subir la imagen.html')            



def project_findings_comment(request, project_id, finding_id):
    finding = get_object_or_404(Finding, id=finding_id)

    if request.method == 'POST':
        # Obtiene el texto del comentario
        text = request.POST.get('text', '').strip()  # 'strip()' elimina espacios en blanco

        # Solo guarda el comentario si hay texto
        if text:
            comment = Comment(
                finding_id=finding,
                user_id=request.user,
                text=text,
            )
            comment.save()  # Guarda el comentario en la base de datos

        return redirect('project_findings', project_id=project_id)  # Redirige a la página de hallazgos del proyecto

    return render(request, 'project_findings.html', {'finding': finding})
      

def project_findings_change_status(request, project_id, finding_id):
    # Obtiene el hallazgo por su ID
    finding = get_object_or_404(Finding, id=finding_id)
    
    # Cambia el estado del hallazgo
    finding.status = not finding.status  # Cambia el estado de True a False o viceversa
    finding.save()  # Guarda el hallazgo actualizado

    # Redirige de vuelta a la página del proyecto o a donde necesites
    return redirect('project_findings', project_id=project_id)

def project_findings_report(request):
    # Obtener la fecha de hoy
    today = datetime.today()

    # Si hoy es lunes, restamos solo 7 días para obtener el lunes de la semana pasada
    if today.weekday() == 0:
        last_monday = today - timedelta(days=7)
    else:
        # Si no es lunes, restamos los días necesarios para llegar al lunes de la semana pasada
        last_monday = today - timedelta(days=today.weekday() + 7)

    # Encontrar el domingo de la semana pasada
    last_sunday = last_monday + timedelta(days=6)

# Filtrar los hallazgos creados entre el lunes y el domingo de la semana pasada
    finding_classifications = FindingClassification.objects.all()
    projects = Project.objects.all()
    
    # Crear una lista que contenga todas las combinaciones de proyectos y clasificaciones con la cantidad de hallazgos
    project_findings = []
    project_grades = []
    project_relevant_findings = []
    grade_data = []
    
    for project in projects:
        project_grade = 100
        #Listado de findings
        for finding_classification in finding_classifications:
            finding_amount = Finding.objects.filter(
                project_id=project.id,
                finding_classification_id=finding_classification.id, created_at__gte=last_monday,  # Desde el lunes de la semana pasada
                created_at__lt=last_sunday + timedelta(days=1) 
            ).count()
            
            ponderated_finding=(finding_amount*finding_classification.weighting)
            
            project_findings.append({
                "project": project,
                "finding_classification": finding_classification,
                "finding_amount": finding_amount,
                "ponderated_finding": ponderated_finding
            })
            project_grade = project_grade - ponderated_finding
       #Calidicaciones
        project_grades.append({
            "project": project,
            "project_grade": project_grade
        })
        
        #Findings relevantes
        critical_findings =  Finding.objects.filter(
        project__id=project.id,
        finding_classification__weighting=6,
        created_at__gte=last_monday,  # Desde el lunes de la semana pasada
        created_at__lt=last_sunday + timedelta(days=1) 
        ).order_by('-created_at')[:3]  
        
        warning_findings = Finding.objects.filter(
        project__id=project.id,
        finding_classification__weighting=3,
        created_at__gte=last_monday,  # Desde el lunes de la semana pasada
        created_at__lt=last_sunday + timedelta(days=1) 
        ).order_by('-created_at')[:3]  
        
        project_relevant_findings.append({"project": project, "critical_findings": critical_findings, "warning_findings": warning_findings})
        
        #Calidicaciones para la tabla
        grade_data.append({
            "project": project.name,
            "project_grade": project_grade
        })
        
    context = {
        "projects": projects,
        "finding_classifications": finding_classifications,
        "project_findings": project_findings,
        "project_grades": project_grades,
        "grade_data": grade_data,
        "project_relevant_findings": project_relevant_findings
    }
    print (project_grades)
    return render(request, 'project_findings_report.html', context)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="project_findings_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar PDF')
    return response

def project_findings_report_download(request):
    # Obtener la fecha de hoy
    today = datetime.today()
    
    # Calcular el lunes de la semana pasada
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)

    finding_classifications = FindingClassification.objects.all()
    projects = Project.objects.all()
    
    project_findings = []
    project_grades = []
    project_relevant_findings = []
    
    for project in projects:
        project_grade = 100
        
        for finding_classification in finding_classifications:
            finding_amount = Finding.objects.filter(
                project_id=project.id,
                finding_classification_id=finding_classification.id,
                created_at__gte=last_monday,
                created_at__lt=last_sunday + timedelta(days=1) 
            ).count()
            
            ponderated_finding = (finding_amount * finding_classification.weighting)
            
            project_findings.append({
                "project": project,
                "finding_classification": finding_classification,
                "finding_amount": finding_amount,
                "ponderated_finding": ponderated_finding
            })
            project_grade -= ponderated_finding
        
        project_grades.append({
            "project": project,
            "project_grade": project_grade
        })
        
        # Hallazgos relevantes
        critical_findings = Finding.objects.filter(
            project__id=project.id,
            finding_classification__weighting=6,
            created_at__gte=last_monday,
            created_at__lt=last_sunday + timedelta(days=1)
        ).order_by('-created_at')[:3]
        
        warning_findings = Finding.objects.filter(
            project__id=project.id,
            finding_classification__weighting=3,
            created_at__gte=last_monday,
            created_at__lt=last_sunday + timedelta(days=1)
        ).order_by('-created_at')[:3]
        
        project_relevant_findings.append({
            "project": project,
            "critical_findings": critical_findings,
            "warning_findings": warning_findings
        })

    context = {
        "projects": projects,
        "finding_classifications": finding_classifications,
        "project_findings": project_findings,
        "project_grades": project_grades,
        "project_relevant_findings": project_relevant_findings
    }
    
    return render_to_pdf('project_findings_report_download.html', context)