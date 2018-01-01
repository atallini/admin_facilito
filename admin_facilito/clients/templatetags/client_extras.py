from django import template

def title_say_hi(username):
    return 'Hola usuario: ' + username.title()

#funcion que devuelve todos los campos de un modelo
def list_fields(model):
    #este return devuelve todos los campos, menos id y todo campo q sea una relacion con otra tabla
    return [field.name for field in model._meta.get_fields() if not field.is_relation and field.name != 'id']

def get_value(model, value):
	return getattr(model, value)

register = template.Library()  #permite trabajar con las funciones dentro del template dentro de html
register.filter('saluda', title_say_hi) #primer parametro es el nombre q se usa dentro del html
register.filter('list_fields', list_fields)
register.filter('get_value', get_value)