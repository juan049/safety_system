from django import forms
from .models import Finding, ProjectContractor, FindingClassification

class FindingRegisterForm(forms.ModelForm):
    class Meta:
        model = Finding
        fields = ['title', 'description', 'finding_classification', 'contractor', 'before_image']
        labels = {
            'title': 'Hallazgo',
            'description': 'Descripción del Hallazgo',
            'finding_classification': 'Clasificación del Hallazgo',
            'contractor': 'Contratista',
            'before_image': 'Fotografía',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Proporcione más detalles sobre el hallazgo'}),
            'finding_classification': forms.HiddenInput(),  # Campo oculto
            'contractor': forms.Select(attrs={'class': 'form-control'}),
            'before_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)  # Recibe project_id como parámetro adicional
        finding_classification_id = kwargs.pop('finding_classification_id', None)  # Recibe finding_classification_id

        super(FindingRegisterForm, self).__init__(*args, **kwargs)

        # Llenar las opciones de clasificación de hallazgo
        finding_classifications = FindingClassification.objects.all()
        self.fields['finding_classification'].choices = [(fc.id, fc.title) for fc in finding_classifications]

        # Si se recibe un ID de clasificación de hallazgo, se establece
        if finding_classification_id:
            self.fields['finding_classification'].initial = finding_classification_id
            
            
        # Llenar las opciones de contratistas
        if project_id:
            project_contractors = ProjectContractor.objects.filter(project_id=project_id)
            self.fields['contractor'].choices = [(pc.contractor.id, pc.contractor.name) for pc in project_contractors]
