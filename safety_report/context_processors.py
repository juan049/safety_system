from .models import Project

def global_variables(request):
    return {
        'projects': Project.objects.all(),
    }