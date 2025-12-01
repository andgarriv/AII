from django.contrib import admin
from django.urls import path
from django1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio),
    path('carga/',views.carga),
]
