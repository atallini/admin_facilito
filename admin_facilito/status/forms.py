from django import forms
from .models import Status

class StatusChoiceForm(forms.Form):
    # combo de seleccion, se rellena con la tabla asociada.
    #recibe conm parametro un cursor
    status = forms.ModelChoiceField(queryset=Status.objects.all(), initial=0)

    def __init__(self, *args, **kwargs):
        super(StatusChoiceForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'browser-default'})