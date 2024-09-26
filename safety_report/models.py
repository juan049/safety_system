from django.db import models
from django.contrib.auth.models import User

# Proyectos
class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self) -> str:
        return self.name

class FindingClassification(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self) -> str:
        return self.title

# Contratistas
class Contractor(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self) -> str:
        return self.name

#Imagenes
class Image(models.Model):
    path = models.CharField(max_length=250)
    image_name = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.image_name        
    
#Tabla con los usuarios registrados en cada proyecto
class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.project.name + ' - ' + self.user.get_username()

#Tabla de los contratistas registrados por proyecto
class ProjectContractor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.project.name + ' - ' #+ self.contractor.name


    
#Hallazgos
class Finding(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, default='', on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    finding_classification = models.ForeignKey(FindingClassification, on_delete=models.CASCADE, default=1)
    before_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='before_image', )
    after_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='after_image', default=None, blank=True, null=True)
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.title
    
    def get_finding_classification(self):
        return self.finding_classification
    
    def get_contractor(self):
        return self.contractor


    
#Comentarios
class Comment(models.Model):
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    before_comment = models.BooleanField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    