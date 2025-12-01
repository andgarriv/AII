from django.urls import path
from . import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('cargarBD/', views.cargarBD, name='cargarBD'),
    path('vinos_por_denominacion/', views.vinos_por_denominacion, name='vinos_por_denominacion'),
    path('vinos_por_anyo/', views.vinos_por_anyo, name='vinos_por_anyo'),
    path('vinos_por_uvas/', views.vinos_por_uvas, name='vinos_por_uvas'),
]
