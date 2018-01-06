from django.shortcuts import render
from django.shortcuts import redirect

from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Project
from .models import ProjectUser
from .models import ProjectPermission
from .forms import CreateProjectForm
from .forms import PermisionProject

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from django.views.generic import DetailView
from status.models import Status

from django.shortcuts import get_object_or_404
#from status.forms import StatusChoiceForms

from status.forms import StatusChoiceForm
from django.contrib import messages
from django.db import transaction

from django.contrib.auth.models import User

# Create your views here.
class CreateClass(LoginRequiredMixin, CreateView):
    #success_url = reverse_lazy('client:dashboard') #anulado por q ira por slug
    login_url = 'client:login'
    template_name = 'project/create.html'  #pendiente
    model = Project
    form_class = CreateProjectForm  #pendiente


    #transaction atomic, ante un error hace un rollback si todo ok hace un commit
    @transaction.atomic
    def  create_objects(self):
        #Se asigna el usuario, que ya lo tiene request user logueado
        #anulado self.object.user = self.request.user

        self.object.save()

        #Despues del save
        #Cada vez que se cree un proyecto, se le asigna un status por default.
        ##aqui indicamos q cree un registro en esta tabla
        self.object.projectstatus_set.create(status=Status.get_defult_status())
        #self.object.projectuser_set.create(user=self.request.user, permission_id=1) #1=fundador

        self.object.projectuser_set.create(user=self.request.user,
                                           permission_id=ProjectPermission.founder_permission()
                                           ) #1=fundador



    def form_valid(self, form):
        self.object = form.save(commit=False) #no se graba, por que hay que asignar el usuario a mano
        self.create_objects()
        #return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(self.get_url_project())


    #cada vez que se cree un proyecto, debe crearse un registro en status por default
    def get_url_project(self):
        return reverse_lazy('projects:show', kwargs = {'slug':self.object.slug})

#Esta clase lista todos los proyectos, de todos los usuarios, no solo el autenticado
class ListClass(LoginRequiredMixin, ListView):
    login_url = 'client:login'
    template_name = 'project/index.html'

    #al heredar de listview, disponemos del metodo get_queryset, este metodo se encarga de realizar
    #el query correspondiente a nuestra base de datos y regrasa un cursor con todos nuestros registros
    def get_queryset(self):
        #anulado return Project.objects.filter(user=self.request.user).order_by('dead_line')
        return Project.objects.all()

class ListMyProjectClass(LoginRequiredMixin, ListView):
    login_url = 'client:login'
    template_name = 'project/mine.html'

    #al heredar de listview, disponemos del metodo get_queryset, este metodo se encarga de realizar
    #el query correspondiente a nuestra base de datos y regrasa un cursor con todos nuestros registros
    def get_queryset(self):
        #anulado return Project.objects.filter(user=self.request.user).order_by('dead_line')
        return ProjectUser.objects.filter(user = self.request.user)


class ShowClass(DetailView):
    model = Project
    template_name = 'project/show.html'

    def get_context_data(self, **kwargs):
        context = super(ShowClass, self).get_context_data(**kwargs)

        if not self.request.user.is_anonymous():
            #nos indica que el usuario si esta autenticado
            #le pasamos una variable al template html
            context['has_permission'] = self.object.user_has_permission(self.request.user)

        return context


"""
Functions
"""
def admin_only(function):
    def wrap(request, *args, **kwargs):
        project = get_object_or_404(Project,slug=kwargs['slug'])
        if not project.user_has_permission(request.user):
            lazy = reverse_lazy('project:show', kwargs={'slug': project.slug})
            return HttpResponseRedirect(lazy)
        return function(request, *args, **kwargs)
    return wrap

@login_required(login_url='client:login')
@admin_only
def edit(request, slug=''):
    # Esta funcion: get_object_or_404, regresa una instancia del modelo, en este caso project
    #  o devuelve un error 404 si no se pudo encontrar el recurso en la base de datos.
    # El segundo parametro es la condicional, le decimos que busque en Project el slug, que nos estan
    # mandando dentro de la url y como parametro de la funcion.
    project = get_object_or_404(Project, slug=slug)

    #Validar que el usuario tenga permisos para acceder a edit, caso contrario, se redirige a show
    """"
    if not project.user_has_permission(request.user):
        lazy = reverse_lazy('projects:show', kwargs={'slug':project.slug})
        return HttpResponseRedirect(lazy)
    """

    form_project = CreateProjectForm(request.POST or None, instance = project)
    forms_status = StatusChoiceForm(request.POST or None,
                                    initial={'status':project.get_id_status()
                                             })

    if request.method == 'POST':
        if form_project.is_valid() and forms_status.is_valid():
            selection_id = forms_status.cleaned_data['status'].id


            form_project.save()  #almacenamos el primer bloque, incluye titulo, descripcion y fecha

            if selection_id != project.get_id_status():
                #ahora necesito decirle, como necesito almacenar los status del proyecto
                project.projectstatus_set.create(status_id = selection_id)

            messages.success(request, 'Datos actualizados correctamente.')



    context = {'form_project':form_project,
               'forms_status':forms_status
               }

    return render(request, 'project/edit.html', context)


class ListContributorsClass(ListView):
    template_name = 'project/contributors.html'
    print('##################################################')
    print('### Ingrese a la funcion  ListContributorsClass')
    print('##################################################')

    def get_queryset(self):
        #se asigna a la variable project, el modelo Project mas el slug, que viene en la url
        self.project = get_object_or_404(Project, slug=self.kwargs['slug'])
        return ProjectUser.objects.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super(ListContributorsClass, self).get_context_data(**kwargs)
        context['project'] = self.project
        return context


@login_required(login_url='client:login')
@admin_only
def add_contributor(request, slug, username):
    project = get_object_or_404(Project, slug=slug)
    user = get_object_or_404(User, username=username)

    print('##############################################')
    print('#### Ingrese a la funcion add_contributor')
    print('slug: ' + slug)
    print('usuario: ' + username)
    print('##############################################')

    """"
    if not project.user_has_permission(request.user):
        lazy = reverse_lazy('projects:show', kwargs={'slug': project.slug})
        #return redirect('project:contributors', slug=project.slug)
        print('*** Error: sali por no tener permisos para efectuar el create.')
        return HttpResponseRedirect(lazy)
    """

    #Aqui hacemos una consulta a la base de datos, tabla projecto, y pregunto si ya existe para
    #el proyecto un usuario asignado con ese nombre, si no existe, que lo de de alta.
    """"
    if not project.projectuser_set.filter(user=user).exists():
        project.projectuser_set.create(user=user,
                                       permission=ProjectPermission.contributor_permission()
                                       )
        #project.projectuser_set.user=user, permission_id=1)
    """
    if project.projectuser_set.filter(user=user).exists():
        print('* Error: ya existe el usuario asignado para el proyecto.')
    else:
        project.projectuser_set.create(user=user,
            permission=ProjectPermission.contributor_permission()
            )
        #project.projectuser_set.create(user=user, permission_id=1)
        print('* OK: Se agrego el usuario al proyecto.')

    print('#############################################')
    print('### FIN DE LA FUNCION ADD_CONTRIBUTOR  99877')
    print('#############################################')

    return redirect('projects:contributors', slug=project.slug)


@login_required(login_url='client:login')
def user_contributor(request, slug, username):
    project = get_object_or_404(Project, slug=slug)
    user = get_object_or_404(User, username=username)
    has_permission = project.user_has_permission(request.user)
    permission = get_object_or_404(ProjectUser, user=user, project=project)

    form = PermisionProject(request.POST or None,
                            initial={'permission': permission.permission_id})

    if request.method == 'POST' and form.is_valid():
        selection_id = form.cleaned_data['permission'].id

        # logica del negocio, aqui se ponen las modificaciones
        if selection_id != permission.id and permission.valida_change_permission():
            permission.permission_id = selection_id
            permission.save()
            messages.success(request, 'Datos actualizados correctamente.')

    context = {
                'project':project,
                'user': user,
                'has_permission' : has_permission,
                'form' : form,
                }

    return render(request, 'project/contributor.html', context)


@login_required(login_url='client:login')
@admin_only
def delete_contributor(request, slug, username):
    project = get_object_or_404(Project, slug=slug)
    user = get_object_or_404(User, username=username)
    project_user = get_object_or_404(ProjectUser, user=user, project=project)

    if not project_user.is_founder():
        project_user.delete()
        print('* OK: Registro eliminado.')
    else:
        print('* Error: no se pudo eliminar registro.')

    return redirect('projects:contributors', slug=project.slug)