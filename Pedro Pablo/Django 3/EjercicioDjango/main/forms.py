from django import forms
from .models import Uva

class UvaChoiceForm(forms.Form):
    uva = forms.ModelChoiceField(
        queryset=Uva.objects.all().order_by('nombre'),
        empty_label="-- Selecciona un tipo de uva --",
        label="Tipo de Uva"
    )
