from django.urls import path
from . import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('ultima_temporada/', views.ultima_temporada, name='ultima_temporada'),
    path('equipos/', views.equipos, name='equipos'),
    path('equipo/<str:equipo_nombre>/', views.detalle_equipo, name='detalle_equipo'),
    path('cinco_estadios_mas_grandes/', views.cinco_estadios_mas_grandes, name='cinco_estadios_mas_grandes'),
    path('cargar/', views.cargar, name='cargar'),
]
