from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Project)
admin.site.register(FindingClassification)
admin.site.register(Contractor)
admin.site.register(ProjectUser)
admin.site.register(ProjectContractor)

#Estos son temporales y los borraré
admin.site.register(Finding)