from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index.html', views.index),
    path('populate', views.populateDatabase),
    path('loadRS', views.loadRS),
    path('ingresar', views.ingresar),  
    path('recomendar_peliculas_usuarios', views.recomendar_peliculas_usuario_RSusuario),  
    path('recomendar_peliculas_usuarios_items', views.recomendar_peliculas_usuario_RSitem),
    path('recomendar_usuarios_peliculas', views.recomendar_usuarios_peliculas),
    path('peliculas_similares', views.peliculas_similares),
    path('puntuaciones_usuario', views.mostrar_usuario)

]
