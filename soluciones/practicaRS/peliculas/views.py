from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Pelicula, Puntuacion
from django.db.models import Count
import csv
import shelve

from .reccomendations import transformPrefs, calculateSimilarItems, topMatches


# Homepage con un menú y botones
def homepage(request):
    return render(request, 'homepage.html')


def cargar_datos(request):
    if request.method == 'POST':
        Pelicula.objects.all().delete()
        Puntuacion.objects.all().delete()

        try:
            # Cargar películas
            with open('data/movies2.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    Pelicula.objects.create(
                        idPelicula=row[0],
                        titulo=row[1],
                        director=row[2],
                        idIMDB=row[3],
                        generos=row[4]
                    )

            # Cargar puntuaciones
            with open('data/ratings.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    if (10 <= int(row[2]) <= 50) and (int(row[2]) % 5 == 0):
                        Puntuacion.objects.create(
                            idUsuario=row[0],
                            pelicula_id=row[1],
                            puntuacion=row[2]
                        )

            peliculas_count = Pelicula.objects.count()
            puntuaciones_count = Puntuacion.objects.count()

            return render(request, 'resultado.html', {
                'peliculas_count': peliculas_count,
                'puntuaciones_count': puntuaciones_count
            })
        except Exception as e:
            return HttpResponse(f"Error al cargar datos: {e}", status=500)
    else:
        return render(request, 'confirmar.html')


def peliculas_por_genero(request):
    # Obtener géneros únicos de la base de datos
    generos = set()
    for pelicula in Pelicula.objects.all():
        for genero in pelicula.generos.split(','):
            generos.add(genero.strip())

    context = {'generos': sorted(list(generos))}

    # Si se ha enviado el formulario
    if request.method == 'POST':
        genero_seleccionado = request.POST.get('genero')

        # Filtrar películas por género seleccionado
        peliculas_filtradas = Pelicula.objects.filter(generos__icontains=genero_seleccionado)

        # Agrupar películas por director
        peliculas_por_director = {}
        for pelicula in peliculas_filtradas:
            director = pelicula.director
            if director not in peliculas_por_director:
                peliculas_por_director[director] = []
            peliculas_por_director[director].append(pelicula)

        context['genero_seleccionado'] = genero_seleccionado
        context['peliculas_por_director'] = peliculas_por_director

    return render(request, 'peliculas_por_genero.html', context)


def peliculas_mas_puntuadas(request):
    # Obtener las dos películas con más puntuaciones
    peliculas_top = Puntuacion.objects.values('pelicula_id').annotate(
        num_puntuaciones=Count('id')
    ).order_by('-num_puntuaciones')[:2]

    # Obtener los detalles de las dos películas más puntuadas
    peliculas_info = []
    for pelicula_data in peliculas_top:
        pelicula = Pelicula.objects.get(idPelicula=pelicula_data['pelicula_id'])
        num_puntuaciones = pelicula_data['num_puntuaciones']
        shelf = shelve.open('dataRS.dat')
        ItemsPrefs = shelf['ItemPrefs']
        shelf.close()
        parecidas = topMatches(ItemsPrefs, pelicula.idPelicula, n=3)
        peliculas = []
        similaridad = []
        for item in parecidas:
            peliculas.append(Pelicula.objects.get(idPelicula=item[1]))
            similaridad.append(item[0])
        items = zip(peliculas, similaridad)

        peliculas_info.append({
            'pelicula': pelicula,
            'num_puntuaciones': num_puntuaciones,
            'items': items
        })

    return render(request, 'peliculas_mas_puntuadas.html', {'peliculas_info': peliculas_info})


def load_dict():
    prefs = {}
    shelf = shelve.open('dataRS.dat')
    ratings = Puntuacion.objects.all()
    for rating in ratings:
        user = int(rating.idUsuario)
        item_id = int(rating.pelicula_id)
        score = int(rating.puntuacion)
        prefs.setdefault(user, {})
        prefs[user][item_id] = score
    shelf['Prefs'] = prefs
    shelf['ItemPrefs'] = transformPrefs(prefs)
    shelf['ItemMatch'] = calculateSimilarItems(prefs)
    shelf.close()


def cargar_recsys(request):
    load_dict()
    return redirect('homepage')
