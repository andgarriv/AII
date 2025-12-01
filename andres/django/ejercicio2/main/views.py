from django.shortcuts import render
from populateDB import populate
from .models import Vino, Denominacion, Uva
from django.db.models import Count, Prefetch


# Create your views here.
def inicio(request):
    vinos = Vino.objects.all().order_by('nombre')
    context = {
        'vinos': vinos
    }
    return render(request, 'inicio.html', context)


def cargarBD(request):
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            num_paises, num_denominaciones, num_uvas, num_vinos = populate()
            mensaje = f"Se han cargado {num_paises} países, {num_denominaciones} denominaciones, {num_uvas} uvas y {num_vinos} vinos."
            return render(request, 'cargarBD.html', {'mensaje': mensaje})
    return render(request, 'cargarBD.html')


def vinos_por_denominacion(request):
    denominaciones = Denominacion.objects.annotate(
        num_vinos=Count('vino')
    ).prefetch_related(
        Prefetch('vino_set', queryset=Vino.objects.order_by('nombre'))
    ).order_by('nombre')

    return render(request, 'vinos_por_denominacion.html', {'denominaciones': denominaciones})


def vinos_por_anyo(request):
    import re
    años_set = set()
    for nombre in Vino.objects.values_list('nombre', flat=True):
        m = re.search(r'\b(18|19|20)\d{2}\b', nombre)
        if m:
            años_set.add(m.group(0))
    years = sorted(años_set, reverse=True)

    vinos = []
    anyo = ''
    mensaje = ''
    if request.method == 'POST':
        anyo = request.POST.get('anyo_select')
        if anyo:
            vinos = Vino.objects.filter(nombre__icontains=anyo).select_related('denominacion').order_by('nombre')
            if not vinos:
                mensaje = f"No se encontraron vinos para el año {anyo}."

    return render(request, 'vinos_por_anyo.html', {
        'vinos': vinos,
        'anyo': anyo,
        'mensaje': mensaje,
        'years': years,
    })


def vinos_por_uvas(request):
    uvas = Uva.objects.all().order_by('nombre')

    if request.method == 'POST':
        uva = request.POST.get('uva_select')
        if uva:
            vinos = Vino.objects.filter(uvas__nombre=uva).order_by('nombre')
            return render(request, 'vinos_por_uvas.html', {
                'uvas': uvas,
                'vinos': vinos,
                'uva_seleccionada': uva,
            })

    return render(request, 'vinos_por_uvas.html', {'uvas': uvas})
