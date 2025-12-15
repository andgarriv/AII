from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('cargar/', views.cargar_datos, name='cargar_datos'),
    path('peliculas_por_genero/', views.peliculas_por_genero, name='peliculas_por_genero'),
    path('peliculas_mas_puntuadas/', views.peliculas_mas_puntuadas, name='peliculas_mas_puntuadas'),
    path('cargar_recsys/', views.cargar_recsys, name='cargar_recsys'),

]
