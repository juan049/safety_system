from django.db import models
from django.contrib.auth.models import User
import uuid

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from io import BytesIO
import fitz  # PyMuPDF para extraer imágenes de PDFs

def get_pdf_image_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    return f"projects/pdf_images/{unique_filename}"


def get_image_path(instance, filename):
    # Generar un UUID y concatenar con la extensión del archivo
    ext = filename.split('.')[-1]  # Obtener la extensión del archivo
    unique_filename = f"{uuid.uuid4()}.{ext}"  # Crear un nombre único
    return f"findings/{unique_filename}"  #

# Modelo Project
import uuid
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image
import fitz  # PyMuPDF
from io import BytesIO

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    pdf_plan = models.FileField(upload_to="projects/plans/", null=True)
    pdf_image = models.ImageField(upload_to="projects/pdf_images/", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generar un nombre único para el PDF
        if self.pdf_plan:
            # Crear un nuevo nombre para el archivo PDF
            new_pdf_name = f"{uuid.uuid4()}.pdf"
            self.pdf_plan.name = new_pdf_name

        # Guarda la instancia primero para asegurarte de que el archivo PDF esté disponible
        super().save(*args, **kwargs)

        # Si se carga un PDF y no hay imagen previa, se genera la imagen
        if self.pdf_plan and not self.pdf_image:
            self.pdf_image = self.convert_pdf_to_image(self.pdf_plan)

            # Vuelve a guardar el modelo con la imagen generada
            super().save(*args, **kwargs)

    def convert_pdf_to_image(self, pdf_file):
        # Abrir el archivo PDF con PyMuPDF
        pdf_doc = fitz.open(pdf_file.path)
        page = pdf_doc.load_page(0)  # Cargar la primera página
        pix = page.get_pixmap()  # Convertir la página a una imagen
        
        # Convertir la imagen a formato PIL
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_io = BytesIO()
        img.save(img_io, format="PNG", optimize=True)

        # Crear un ContentFile con la imagen generada usando un UUID
        new_image_name = f"{uuid.uuid4()}.png"
        new_image = ContentFile(img_io.getvalue(), name=new_image_name)
        return new_image


class FindingClassification(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    weighting = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.title

# Contratistas
class Contractor(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self) -> str:
        return self.name      
    
#Tabla con los usuarios registrados en cada proyecto
class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.project.name + ' - ' + self.user.first_name + ' ' + self.user.last_name

#Tabla de los contratistas registrados por proyecto
class ProjectContractor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.project.name + ' - ' #+ self.contractor.name


    
class Finding(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, default='', on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    finding_classification = models.ForeignKey(FindingClassification, on_delete=models.CASCADE)
    
    # Usar la función get_image_path para el campo before_image
    before_image = models.ImageField(upload_to=get_image_path, blank=False, null=False) 
    
    # La segunda imagen es opcional
    after_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Nuevo campo para el autor (quien creó el hallazgo)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Nuevos campos para las coordenadas
    pin_x = models.FloatField(null=True, blank=True)  # Coordenada X
    pin_y = models.FloatField(null=True, blank=True)  # Coordenada Y
    
    # Sobrescribir el método save para redimensionar y comprimir las imágenes
    def save(self, *args, **kwargs):
        # Redimensionar y comprimir la imagen antes (before_image)
        if self.before_image:
            self.before_image = self.optimize_image(self.before_image, (500, 300))

        # Redimensionar y comprimir la imagen después (after_image) si existe
        if self.after_image:
            self.after_image = self.optimize_image(self.after_image, (500, 300))
        
        super().save(*args, **kwargs)

    def optimize_image(self, image_field, size):
        # Abrir la imagen utilizando Pillow
        img = Image.open(image_field)
        
        # Convertir a formato RGB si es necesario (para JPEG)
        if img.mode in ("RGBA", "P"):  # Convertir si la imagen tiene transparencia
            img = img.convert("RGB")
        
        # Redimensionar la imagen
        img = img.resize(size, Image.LANCZOS)

        # Eliminar metadatos para reducir el tamaño
        img = ImageOps.exif_transpose(img)  # Se asegura que las rotaciones se apliquen y los EXIF se descarten
        
        # Guardar la imagen en un objeto BytesIO con formato JPEG
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85, optimize=True)  # Optimiza y ajusta calidad

        # Crear un nuevo ContentFile con la imagen optimizada
        new_image = ContentFile(img_io.getvalue(), name=image_field.name)
        return new_image

    def __str__(self) -> str:
        return self.title
    
    def get_finding_classification(self):
        return self.finding_classification
    
    def get_contractor(self):
        return self.contractor
    
#Comentarios
class Comment(models.Model):
    finding_id = models.ForeignKey(Finding, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    