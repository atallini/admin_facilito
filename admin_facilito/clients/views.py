from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import redirect

from django.http import HttpResponse, HttpResponseRedirect

from clients.forms import LoginUserForm

from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django

from django.contrib.auth.decorators import login_required

from clients.forms import CreateUserForm
from clients.forms import EditUserForm
from clients.forms import EditPasswordForm
from clients.forms import EditClientForm
from clients.forms import EditClientSocial


from django.views.generic import View
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from django.contrib.auth import update_session_auth_hash
from django.contrib import messages  #se utiliza para mensajes error en funciones
from django.contrib.messages.views import SuccessMessageMixin #se utiliza para mensajes en clases

from .models import Client
from .models import SocialNetwork

from django.core import serializers

import json

class EditView(UpdateView, SuccessMessageMixin):
    login_url = 'client.login'
    model = User
    template_name = 'client/edit.html'
    success_url = reverse_lazy('client:edit')
    form_class = EditUserForm
    success_message = 'Tu usuario ha sido actualizado con exito.'

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EditView, self).form_valid(request, *args, **kwargs)

    #aqui estamos indicando que no vamos a realizar ningun tipo de query, por q vamos a utilizar
    #el usuario que devuelve firmado, el que se encuentra dentro de request / user
    def get_object(self, queryset=None):
        return self.request.user


# Create your views here.
def show(request):
    return HttpResponse("Hola mundo querido por anibal")

class CreateView(CreateView):
    #success_url = 'client:login'  #aqui obtenemos la url, pero sin el local host
    success_url = reverse_lazy('client:login') #aqui obtenemos la url completa, con el dominio localhost
    template_name = 'client/create.html'
    model = User
    form_class = CreateUserForm

    #hay q sobreescribir este metodo, por que hay que encriptar la password
    #debe devolver siempre un httpresponse, en este caso se redirecciona a success_url
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_password(self.object.password)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ShowView(DetailView):
    model = User
    template_name = 'client/show.html'
    slug_field = 'username'  #indica el campo de la tabla
    slug_url_kwarg = 'username_url'  #que atributo de la url


class LoginView(View):
    form = LoginUserForm()
    message = None
    template = 'client/login.html'

    #como heredamos de view, podemos hacer un metodo de tipo get, que se activa al hacer el request
    #get recibe el request, los argumentos args y el diccionario de argumentos kwargs
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('client:dashboard')
        return render(request, self.template, self.get_context())

    #como heredamos de view, podemos hacer un metodo de tipo post, que se activa al hacer el request
    #get recibe el request, los argumentos args y el diccionario de argumentos kwargs
    def post(self, request, *args, **kwargs):
        username_post = request.POST['username']
        password_post = request.POST['password']
        user = authenticate(username = username_post, password=password_post)

        if user is not None:
            login_django(request, user)
            return redirect('client:dashboard')
        else:
            self.message='Usuario o clave incorrecta.'
        return render(request, self.template, self.get_context())

    def get_context(self):
        return {'form':self.form, 'message':self.message}


class DashboardView(LoginRequiredMixin, View):
    login_url ='client:login'  #determina a q url redirigir, si el usuario NO ESTA LOGUEADO

    print('### hola mundo anibal ....')

    def get(self, request, *args, **kwargs):
        return render(request, 'client/dashboard.html', {})


def login_dos(request):
    if request.user.is_authenticated():
        return redirect('client:dashboard')

    message = None
    if request.method == 'POST': #nos estan enviando el formulario
        username_post = request.POST['username']
        password_post = request.POST['password']

        user = authenticate(username = username_post, password=password_post)
        if user is not None:
            login_django(request, user)
            return redirect('client:dashboard')
        else:
            message='Usuario o clave incorrecta.'

    #print(username)
    #print(password)

    form = LoginForm()
    context = {
        'form':form,
        'message':message
    }
    #nombre = 'anibal'
    #contexto = {'nombre':nombre}
    return render(request, 'client/login.html', context)


@login_required(login_url='client:login')
def dashboard_dos(request):
    if request.user.is_authenticated():
        texto='el usuario esta autenticado'
    return render(request, 'dashboard.html', {})


@login_required(login_url='client:login')
def logout(request):
    logout_django(request)
    return redirect('client:login')


def create(request):
    form = CreateUserForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit = False)
            user.set_password(user.password)
            user.save()
            return redirect('client:login')

    context = {
        'form' : form
    }
    return render(request, 'client/create.html', context)


def edit_password(request):
    form = EditPasswordForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            current_password = form.cleaned_data['password']
            new_password = form.cleaned_data['new_password']

            if authenticate(username = request.user.username, password = current_password):
                request.user.set_password(new_password)
                request.user.save()

                update_session_auth_hash(request, request.user)
                messages.success(request, 'MESSAGE-SUCCESS: La clave fue modificada correctamente.')
            else:
                messages.error(request, 'MESSAGE-ERROR: La clave no pudos ser modificada.')


            #print('el formulario es valido')

    context = {'form': form}
    return render(request,'client/edit_password.html', context)

@login_required(login_url='client:login')
def edit_client(request):

    #form = EditClientForm(request.POST or None, instance = request.user.client )
    form = EditClientForm(request.POST or None, instance = client_instance(request.user) )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos actualizados correctamente.')

    return render(request, 'client/edit_client.html', {'form':form})

#si el usuario contiene un client, entonces voy a regresar ese client, caso contrario, voy a
#regresar una nueva instancia de client.
def client_instance(user):
    try:
        return user.client
    except:
        return Client(user=user)

#En esta funcion, queremos unir las dos vistas usuarios + cliente, que contiene campos extras,
#q deben asociarse a usuario, con una relacion uno a uno
@login_required(login_url='client:login')
def edit_client_unidos(request):

    #Creamos dos variables de tipo form user + client
    form_client = EditClientForm(request.POST or None, instance = client_instance(request.user) )
    form_user = EditUserForm(request.POST or None, instance = request.user )

    if request.method == 'POST':
        if form_client.is_valid() and form_user.is_valid():
            form_user.save()
            form_client.save()
            messages.success(request, 'Datos actualizados correctamente.')

    #Ahora debemos renderizar los dos forms
    context = {
        'form_client': form_client,
        'form_user': form_user
    }

    return render(request, 'client/edit.html', context)


class EditSocialClass(LoginRequiredMixin, UpdateView, SuccessMessageMixin):
    login_url = 'client:login'
    model = SocialNetwork
    template_name = 'client/edit_social.html'
    success_url = reverse_lazy('client:edit_social')
    form_class = EditClientSocial
    success_message = "Tu usuarios ha sido actualizado exitosamente."

    def get_object(self, queryset=None):
        return self.get_social_instance()

    #si el usuario tiene un modelo de redsocial lo retornamos, caso contrario, creamos uno nuevo.
    def get_social_instance(self):
        try:
            return self.request.user.socialnetwork
        except:
            return SocialNetwork(user=self.request.user)


def user_filter(request, username):

    #username = request.GET.get('username', '')
    # select * from users where username like '%username'
    users = User.objects.filter(username__startswith=username)
    users = serializers.serialize('json', users)

    return HttpResponse(users, content_type='application/json')


def user_filter_dos(request, username):
    #username = request.GET.get('username', '')

    # select * from users where username like '%username'
    users = User.objects.filter(username__startswith=username)
    users = [user_serializer(user) for user in users]

    return HttpResponse(json.dumps(users), content_type='application/json')

def user_filter_tres(request):
    # aqui leemos todos los paremetros que vienen en la url, aqui interesa username
    username = request.GET.get('username', '')

    # select * from users where username like '%username'
    users = User.objects.filter(username__startswith=username)
    users = serializers.serialize('json', users)

    return HttpResponse(users, content_type='application/json')


def user_filter_cuatro(request):

    #aqui leemos todos los paremetros que vienen en la url, aqui interesa username
    username = request.GET.get('username', '')

    # select * from users where username like '%username'
    users = User.objects.filter(username__startswith=username)
    users = [user_serializer(user) for user in users]

    return HttpResponse(json.dumps(users), content_type='application/json')

def user_serializer(user):
    return {'id': user.id, 'username': user.username}


def client_instance(user):
    try:
        return user.client
    except:
        return Client(user = user)
