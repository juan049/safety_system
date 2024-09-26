from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import Project, Finding, FindingClassification, Contractor, Image, ProjectContractor

# Create your views here.
def home(request):
    projects = list(Project.objects.all())
    return render(request, 'home.html', {
        "projects": projects
    })

def project_findings(request, id):
    project = get_object_or_404(Project, id=id)
    project_name = project.name
    
    findings = list(Finding.objects.filter(project_id=id))
    findings.reverse()
    print(findings)
    return render(request, 'project_findings.html', {
        "project_id" : id,
        "project_name": project_name,
        "findings": findings
        
    })

def project_findings_register(request, id):
    if request.method == 'POST':
       title = request.POST.get('title', '')
       finding_classification= request.POST.get('finding_classification', '')
       contractor= request.POST.get('contractor', '')
       description   = request.POST.get('description', '')
       
       print( title,  finding_classification, contractor, description)
       
       #creo un finding
       finding = Finding()
       
       finding.title = title
       finding.project = get_object_or_404(Project, id=id)
       finding.finding_classification = get_object_or_404(FindingClassification, id=finding_classification)
       finding.contractor = get_object_or_404(Contractor, id=contractor)
       finding.description=description
       finding.before_image = get_object_or_404(Image, id=id)
       finding.status = False
       finding.save()      
       
       return redirect('http://localhost:8000/project_findings/'+str(id))
            
    #ingreso los contratistas y riesgos
    project_contractors = list(ProjectContractor.objects.filter(project_id=id))
    
    finding_classifications = list(FindingClassification.objects.all())
    return render(request, 'project_findings_register.html', {
        "project_id": id,
        "project_contractors":  project_contractors,
        "finding_classifications": finding_classifications
    })

def project_findings_report(request):
    return render(request, 'project_findings_report.html')