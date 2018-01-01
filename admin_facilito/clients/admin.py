from django.contrib import admin
from .models import Client
from .models import SocialNetwork

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

# Register your models here.

#Para excluir el campo user del modelo Client
class ClientAdmin(admin.ModelAdmin):
    exclude = ('user',)

class ClientInLine(admin.StackedInline):
    model = Client
    can_delete = False

class SocialInLine(admin.StackedInline):
    model = SocialNetwork
    can_delete = False

#quitado el modelo admin, ahora hay q agregar un modelo admin propio unidos con client
class UserAdmin(AuthUserAdmin):
    #inlines = [ClientInLine]
    inlines = [ClientInLine, SocialInLine]

#admin.site.register(Client)
admin.site.unregister(User)  #aqui quitamos el modelo user de nuestro usuario admin
admin.site.register(Client, ClientAdmin)
admin.site.register(User, UserAdmin)