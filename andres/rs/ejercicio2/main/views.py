from django.shortcuts import render
from django.conf import settings
from .populateDB import populate


# Create your views here.
def index(request):
    return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})


def cargarBD(request):
    resultados = populate()
    print(resultados)
    return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})