from django.shortcuts import render, redirect
from main.populateDB import populate
from .models import Vino
from django.db.models import Count
from .forms import UvaChoiceForm

# Create your views here.
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_paises, num_denominaciones, num_uvas, num_vinos = populate()
            mensaje="Se han almacenado: " + str(num_paises) +" paises, " + str(num_denominaciones) +" denominaciones, " + str(num_uvas) +" uvas, " + str(num_vinos) +" vinos"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')


def inicio(request):
    num_vinos=Vino.objects.all().count()
    context={'num_vinos':num_vinos}
    return render(request, 'inicio.html', context)

def vinos_agrupados_por_denominacion(request):
    denominaciones=Vino.objects.values('denominacion__nombre').annotate(total=Count('idVino')).order_by('denominacion__nombre')
    context={'denominaciones':denominaciones}
    return render(request, 'vinos_por_denominacion.html', context)

def vinos_por_anyo(request):
    # Leer el año desde GET (?anyo=2020). Si no hay, mostramos sin resultados.
    anyo = request.GET.get('anyo')
    vinos = []
    if anyo:
        vinos = Vino.objects.filter(nombre__icontains=str(anyo)).order_by('nombre')
    context = {'vinos': vinos, 'anyo': anyo}
    return render(request, 'vinos_por_anyo.html', context)

def vinos_por_uvas(request):
    form = UvaChoiceForm(request.POST or None)
    vinos = None
    seleccion = None

    if request.method == 'POST' and form.is_valid():
        seleccion = form.cleaned_data['uva']   # es un objeto Uva
        vinos = Vino.objects.filter(uvas=seleccion).order_by('nombre')

    context = {
        'form': form,
        'vinos': vinos,
        'seleccion': seleccion,
    }
    return render(request, 'vinos_por_uvas.html', context)