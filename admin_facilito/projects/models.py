from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ValidationError

from django.utils import timezone
from status.models import Status
from django.contrib.auth.models import User



# Create your models here.
class Project(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    dead_line = models.DateField()
    create_date = models.DateField(default=datetime.date.today)
    slug = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.title

    #validar que el slug sea unico
    def validate_unique(self, exclude=None):
        if Project.objects.filter(title=self.title).exclude(pk=self.id).exists():
            raise ValidationError('Un proyecto con el mismo nombre ya esta registrado.')

    def get_id_status(self):
        return self.projectstatus_set.last().status_id

    def get_status(self):
        return self.projectstatus_set.last().status

    def create_slug_field(self, value):
        return value.lower().replace(' ', '_')

    #este metodo retorno verdadero si el usuario tiene permiso, segun la tabla projectpermission
    #primero buscamos en projectuser, para saber si un usuario es colaborador del proyecto

    def user_has_permission(self, user):
        return self.projectuser_set.filter(user=user, permission_id=1).count()>0


    def save(self, *args, **kwargs):
        self.validate_unique()
        self.slug = self.title.replace(" ", "_").lower() #reemplaza espacion por _ y todo minusculas
        super(Project, self).save(*args, **kwargs)


class ProjectStatus(models.Model):
    project = models.ForeignKey(Project)
    status = models.ForeignKey(Status)
    create_date = models.DateTimeField(default = timezone.now)


class ProjectPermission(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    level = models.IntegerField()
    create_date = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.title

    @classmethod
    def founder_permission(cls):
        #este metodo de clase, devuelve un objeto ProjectPermission que corresponde al FUNDADOR
        return ProjectPermission.objects.get(pk=1)

    @classmethod
    def co_founder_permission(cls):
        #este metodo devuelve el COFUNDADOR
        return ProjectPermission.objects.get(pk=2)

    @classmethod
    def contributor_permission(cls):
        #este metodo devuelve el COLABORADOR
        return ProjectPermission.objects.get(pk=3)

    @classmethod
    def admin_permission(cls):
        return [1, 2]

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete = models.CASCADE)
    user = models.ForeignKey(User)
    permission = models.ForeignKey(ProjectPermission)
    create_date = models.DateTimeField(default = timezone.now)

    def get_project(self):
        return self.project

    def is_founder(self):
        return self.permission == ProjectPermission.founder_permission()

    def valida_change_permission(self):
        if not self.is_founder():
            return True
        return self.exists_another_founder()

    def exists_another_founder(self):
        return ProjectUser.objects.filter(project=self.project, permission=ProjectPermission.founder_permission()).exclude(user=self.user).count() > 0