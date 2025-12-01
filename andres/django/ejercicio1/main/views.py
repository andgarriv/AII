from django.shortcuts import render
from .models import Temporada, Jornada, Equipo, Partido
from populateDB import populateDatabase


def inicio(request):
    temporadas = Temporada.objects.all().order_by('-anyo')
    context = {
        'temporadas': temporadas,
    }
    return render(request, 'inicio.html', context)


def ultima_temporada(request):
    temporada = Temporada.objects.all().order_by('-anyo').first()
    jornadas = Jornada.objects.filter(temporada=temporada).order_by('numero')
    context = {
        'temporada': temporada,
        'jornadas': jornadas,
    }
    return render(request, 'ultima_temporada.html', context)


def equipos(request):
    equipos = Equipo.objects.all().order_by('nombre')
    context = {
        'equipos': equipos,
    }
    return render(request, 'equipos.html', context)


def detalle_equipo(request, equipo_nombre):
    equipo = Equipo.objects.get(nombre=equipo_nombre)
    context = {
        'equipo': equipo,
    }
    return render(request, 'detalle_equipo.html', context)


def cinco_estadios_mas_grandes(request):
    equipos = Equipo.objects.all().order_by('-aforo')[:5]
    context = {
        'equipos': equipos,
    }
    return render(request, 'cinco_estadios_mas_grandes.html', context)


def cargar(request):
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            populateDatabase()
            num_temporadas = Temporada.objects.count()
            num_jornadas = Jornada.objects.count()
            num_equipos = Equipo.objects.count()
            num_partidos = Partido.objects.count()
            mensaje = f'Datos cargados correctamente: {num_temporadas} temporadas, {num_jornadas} jornadas, {num_equipos} equipos, {num_partidos} partidos.'
            return render(request, 'cargar.html', {'mensaje': mensaje})
    return render(request, 'cargar.html')
