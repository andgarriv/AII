from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.inicio),
    path('admin/', admin.site.urls),
    path('carga/', views.carga),
    path('vinos_por_denominacion/', views.vinos_agrupados_por_denominacion),
    path('vinos_por_anyo/', views.vinos_por_anyo),
    path('vinos_por_uvas/', views.vinos_por_uvas),
]
