"""
URL configuration for ejercicio1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='inicio'),
    path('index.html', views.index, name='inicio'),
    path('loadRS/', views.loadRS, name='load_rs'),
    path('cargarBD/', views.cargarBD, name='cargar_bd'),
    path('puntuaciones_usuario/', views.mostrar_puntuaciones_usuario, name='puntuaciones_usuario'),
    path('peliculas_similares/', views.mostrar_peliculas_parecidas, name='peliculas_similares'),
    path('recomendar_peliculas_usuarios/', views.recomendar_peliculas_usuario_RSusuario, name='recomendar_peliculas_usuarios'),
    path('recomendar_peliculas_usuarios_items/', views.recomendar_peliculas_usuario_RSitems, name='recomendar_peliculas_usuarios_items'),
    path('recomendar_usuarios_peliculas/', views.recomendar_usuarios_pelicula, name='recomendar_usuarios_peliculas'),
]
