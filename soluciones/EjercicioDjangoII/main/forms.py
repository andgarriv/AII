#encoding:utf-8
from django import forms
from main.models import Genero

   
class BusquedaPorGeneroForm(forms.Form):
    genero = forms.ModelChoiceField(label="Seleccione el género", queryset=Genero.objects.all())
    
class BusquedaPorFechaForm(forms.Form):
    fecha = forms.DateField(label="Fecha (Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'))