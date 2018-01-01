#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from .models import Client
from .models import SocialNetwork

"""
Constantes
"""

ERROR_MESSAGE_USER = {'required':'El username es obligatorio.','unique':'El usuario ya esta registrado','invalid':'Ingrese un usuario correcto.'}
ERROR_MESSAGE_PASSWORD = {'required':'La password es obligatoria.'}
ERROR_MESSAGE_EMAIL = {'required':'El email es obligatorio.','invalid':'Ingrese un correo valido.'}

"""
Funciones
"""
def must_be_gt(value_password):
    if len(value_password) < 5:
        raise forms.ValidationError('Funcion: La clave debe ser mayor a cinco caracteres.')

"""
Clases
"""

#En esta clase veremos dos formas diferentes de hacer validaciones.
#Uno: validar sobreescribiendo validators con un diccionario de funciones, en este caso la funcion
#se llama must_be_gt()
#La segunda opcion es utilizando clean_new_password
class EditPasswordForm(forms.Form):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput())
    new_password = forms.CharField(max_length=20, widget=forms.PasswordInput(), validators=[must_be_gt])
    repeat_password = forms.CharField(max_length=20, widget=forms.PasswordInput(), validators=[must_be_gt])

    #Anulado alternativo, por que esta activado must_be_gt
    #Con clean_ + el nombre del atributo: se utiliza para validar un campo especifico, en este caso el
    #campo password.  Cuando se dispara la validacion ? cuando usamos if form.is_valid() en views
    #def clean_new_password(self):
    #    value_password = self.cleaned_data['new_password']
    #    if len(value_password) < 5:
    #        raise forms.ValidationError('La clave debe ser mayor a cinco caracteres.')
    #    value_password

    #CLEAN NOS PERMITE TRABAJAR CON TODOS LOS CAMPOS DEL FORM PARA VALIDARLOS
    #Este metodo clean no necesita regresar un valor, solo se puede controlar por excepciones
    def clean(self):
        clean_data = super(EditPasswordForm, self).clean()
        password1 = clean_data['new_password']
        password2 = clean_data['repeat_password']

        if password1 != password2:
            raise forms.ValidationError('Error, las password son diferentes.')


class LoginUserForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'id': 'username_login', 'class': 'input_login'})
        self.fields['password'].widget.attrs.update({'id': 'password_login', 'class': 'input_login'})


class CreateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=20,
        error_messages=ERROR_MESSAGE_USER)

    password = forms.CharField(max_length=20, widget=forms.PasswordInput(),
        error_messages=ERROR_MESSAGE_PASSWORD)

    email = forms.CharField(error_messages=ERROR_MESSAGE_EMAIL)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'id': 'username_create'})
        self.fields['password'].widget.attrs.update({'id': 'password_create'})
        self.fields['email'].widget.attrs.update({'id': 'email_create'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).count():
            raise forms.ValidationError('El email debe de ser unico.')
        return email

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class EditUserForm(forms.ModelForm):
    username = forms.CharField(max_length=20,
        error_messages=ERROR_MESSAGE_USER)

    first_name = forms.CharField(label='Nombre completo', required=False)
    last_name = forms.CharField(label='Apellidos', required=False)
    email = forms.CharField(error_messages=ERROR_MESSAGE_EMAIL)

    #password = forms.CharField(max_length=20, widget=forms.PasswordInput(),
    #    error_messages=ERROR_MESSAGE_PASSWORD)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.id).count():
            raise forms.ValidationError('El email debe de ser unico.')
        return email

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class EditClientForm(forms.ModelForm):

	job = forms.CharField(label= "Trabajo actual", required=False)
	bio = forms.CharField(label= "Comentarios", widget=forms.Textarea, required=False)

	class Meta:
		model = Client
        #fields =('bio', 'job')  #que incluya estos dos campos bio y job
		exclude = ['user']  #que excluya solo el campo user e incluya el resto

	def __init__(self, *args, **kwargs):
		super(EditClientForm, self).__init__(*args, **kwargs)
		self.fields['job'].widget.attrs.update({'id': 'job_edit_client', 'class' : 'validate'})
		self.fields['bio'].widget.attrs.update({'id': 'bio_edit_client', 'class' : 'validate'})

class EditClientSocial(forms.ModelForm):
    class Meta:
        model = SocialNetwork
        exclude =['user']