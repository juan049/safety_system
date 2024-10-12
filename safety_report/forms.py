from django import forms
from .models import Finding, Project, ProjectContractor, FindingClassification

class ProjectRegisterForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'pdf_plan']  # Asegúrate de que estos campos existan en el modelo
        labels = {
            'name': 'Nombre del Proyecto',
            'description': 'Descripción',
            'pdf_plan': 'Subir Plano PDF',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proyecto'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del proyecto'}),
            'pdf_plan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
class FindingRegisterForm(forms.ModelForm):
    pin_x = forms.FloatField(widget=forms.HiddenInput(), required=False)  # Campo para coordenada X
    pin_y = forms.FloatField(widget=forms.HiddenInput(), required=False)  # Campo para coordenada Y

    class Meta:
        model = Finding
        fields = ['title', 'description', 'finding_classification', 'contractor', 'before_image', 'pin_x', 'pin_y']
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
            'finding_classification': forms.HiddenInput(),
            'contractor': forms.Select(attrs={'class': 'form-control'}),
            'before_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        finding_classification_id = kwargs.pop('finding_classification_id', None)

        super(FindingRegisterForm, self).__init__(*args, **kwargs)

        # Llenar las opciones de clasificación de hallazgo
        finding_classifications = FindingClassification.objects.all()
        self.fields['finding_classification'].choices = [(fc.id, fc.title) for fc in finding_classifications]

        if finding_classification_id:
            self.fields['finding_classification'].initial = finding_classification_id

        # Llenar las opciones de contratistas
        if project_id:
            project_contractors = ProjectContractor.objects.filter(project_id=project_id)
            self.fields['contractor'].choices = [(pc.contractor.id, pc.contractor.name) for pc in project_contractors]

        # Establecer los valores de las coordenadas si se pasan como parte de kwargs
        if 'pin_x' in kwargs:
            self.fields['pin_x'].initial = kwargs['pin_x']
        if 'pin_y' in kwargs:
            self.fields['pin_y'].initial = kwargs['pin_y']
    def clean(self):
        cleaned_data = super().clean()
        pin_x = cleaned_data.get('pin_x')
        pin_y = cleaned_data.get('pin_y')

        if pin_x is None or pin_y is None:
            raise forms.ValidationError("Las coordenadas son necesarias.")

        return cleaned_data