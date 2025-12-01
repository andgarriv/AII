from django.shortcuts import render
from .models import Temporada, Jornada, Equipo, Partido

# Create your views here.

def inicio(request):
    temporadas=Temporada.objects.all().order_by('anyo')
    context={'temporadas':temporadas}
    return render(request, 'inicio.html', context)

def resultados_partidos_temporada_actual(request):
    temporada=Temporada.objects.all().order_by('anyo').last()
    jornadas= Jornada.objects.filter(temporada=temporada).order_by('numero')
    context={'temporada':temporada, 'jornadas':jornadas}
    return render(request, 'partidos_actual_temporada.html', context)

def lista_equipos(request):
    equipos=Equipo.objects.all().order_by('nombre')
    context={'equipos':equipos}
    return render(request, 'lista_equipos.html', context)

def detalles_equipo(request, equipo_id):
    equipo=Equipo.objects.get(id=equipo_id)
    context={'equipo':equipo}
    return render(request, 'detalles_equipo.html', context)

def top_5_estadios_mas_aforo(request):
    equipos=Equipo.objects.all().order_by('-aforo')[:5]
    context={'equipos':equipos}
    return render(request, 'top_5_estadios.html', context)
