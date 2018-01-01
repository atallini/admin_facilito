from django.contrib import admin
from .models import Project
from .models import ProjectStatus
from .models import ProjectPermission
from .models import ProjectUser

# Register your models here.
class ProjectStatusInLine(admin.TabularInline):
    model = ProjectStatus
    extra = 0
    can_delete = False


class ProjectAdmin(admin.ModelAdmin):
    #como la relacion es de uno a muchos y al heredar de modeladmin, puedo trabajar con campo inline
    #que contiene una lista, donde colocamos las clases con la relacion uno a muchos, en este caso
    #corresponde ProjectStatusInLine.  Esta lista puede contener todas las clases asociadas, con
    #la relacion uno a muchos.
    inlines = [ ProjectStatusInLine, ]


#admin.site.register(Project)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectPermission)
admin.site.register(ProjectUser)