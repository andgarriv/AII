from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import Pelicula, Puntuacion, Usuario 
from .populateDB import populate
from .recommendations import transformPrefs, calculateSimilarItems
import shelve
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from .forms import UsuarioBusquedaForm, PeliculaBusquedaForm
from .recommendations import getRecommendations, getRecommendedItems, topMatches
# Create your views here.

def loadDict():
    Res={}
    shelf = shelve.open("dataRS.dat")
    puntuaciones = Puntuacion.objects.all()
    for p in puntuaciones:
        usuario = int(p.idUsuario.idUsuario)
        pelicula = int(p.idPelicula.idPelicula)
        puntuacion = float(p.puntuacion)
        Res.setdefault(usuario,{})
        Res[usuario][pelicula]=puntuacion
    shelf['Res']=Res
    shelf['ItemsRes']= transformPrefs(Res)
    shelf['SimItems']= calculateSimilarItems(Res, n=10)
    shelf.close()

@login_required(login_url='/ingresar')
def populateDatabase(request):
    populate()
    logout(request)
    return HttpResponseRedirect('/index.html')

def loadRS(request):
    loadDict()
    return HttpResponseRedirect('/index.html')

def index(request):
    return render(request, 'index.html')

def ingresar(request):
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/populate'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

def recomendar_peliculas_usuario_RSusuario(request):
    formulario = UsuarioBusquedaForm()
    usuario = None
    items = None

    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)

        if formulario.is_valid():
            idUsuario = formulario.cleaned_data['idUsuario']
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            shelf = shelve.open("dataRS.dat")
            Res = shelf['Res']
            shelf.close()
            recomendaciones = getRecommendations(Res, int(idUsuario))
            recomendadas = recomendaciones[:2]
            peliculas = []
            puntuaciones = []
            for r in recomendadas:
                peliculas.append(Pelicula.objects.get(pk=r[1]))
                puntuaciones.append(r[0])
            items = zip(peliculas,puntuaciones)
    return render(request, 'recomendaciones_usuario.html', {'formulario':formulario, 'usuario': usuario, 'items': items, 'STATIC_URL':settings.STATIC_URL})


def recomendar_peliculas_usuario_RSitem(request):
    formulario = UsuarioBusquedaForm()
    usuario = None
    items = None

    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)

        if formulario.is_valid():
            idUsuario = formulario.cleaned_data['idUsuario']
            usuario = get_object_or_404(Usuario, pk=idUsuario)
            shelf = shelve.open("dataRS.dat")
            Res = shelf['Res']
            SimItems = shelf['SimItems']
            shelf.close()
            recomendaciones = getRecommendedItems(Res, SimItems, int(idUsuario))
            recomendadas = recomendaciones[:3]
            peliculas = []
            puntuaciones = []
            for r in recomendadas:
                peliculas.append(Pelicula.objects.get(pk=r[1]))
                puntuaciones.append(r[0])
            items = zip(peliculas,puntuaciones)
    return render(request, 'recomendaciones_usuario.html', {'formulario':formulario, 'usuario': usuario, 'items': items, 'STATIC_URL':settings.STATIC_URL})

def recomendar_usuarios_peliculas(request):
    formulario = PeliculaBusquedaForm()
    pelicula = None
    items = None

    if request.method=='POST':
        formulario = PeliculaBusquedaForm(request.POST)

        if formulario.is_valid():
            idPelicula = formulario.cleaned_data['idPelicula']
            pelicula = get_object_or_404(Pelicula, pk=idPelicula)
            shelf = shelve.open("dataRS.dat")
            ItemsRes = shelf['ItemsRes']
            shelf.close()
            recomendaciones = getRecommendations(ItemsRes, int(idPelicula))
            recomendadas = recomendaciones[:3]
            usuarios = []
            puntuaciones = []
            for r in recomendadas:
                usuarios.append(Usuario.objects.get(pk=r[1]))
                puntuaciones.append(r[0])
            items = zip(usuarios,puntuaciones)
    return render(request, 'recomendaciones_pelicula.html', {'formulario':formulario, 'pelicula': pelicula, 'items': items, 'STATIC_URL':settings.STATIC_URL})

def peliculas_similares(request):
    formulario = PeliculaBusquedaForm()
    pelicula = None
    items = None

    if request.method=='POST':
        formulario = PeliculaBusquedaForm(request.POST)

        if formulario.is_valid():
            idPelicula = formulario.cleaned_data['idPelicula']
            pelicula = get_object_or_404(Pelicula, pk=idPelicula)
            shelf = shelve.open("dataRS.dat")
            ItemsRes = shelf['ItemsRes']
            shelf.close()
            recomendaciones = topMatches(ItemsRes, int(idPelicula), n=3)
            peliculas = []
            puntuaciones = []
            for r in recomendaciones:
                peliculas.append(Pelicula.objects.get(pk=r[1]))
                puntuaciones.append(r[0])
            items = zip(peliculas,puntuaciones)
    return render(request, 'peliculas_similares.html', {'formulario':formulario, 'pelicula': pelicula, 'items': items, 'STATIC_URL':settings.STATIC_URL})

def mostrar_usuario(request):
    formulario = UsuarioBusquedaForm()
    puntuaciones = None
    idUsuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idUsuario = formulario.cleaned_data['idUsuario']
            puntuaciones = Puntuacion.objects.filter(idUsuario=Usuario.objects.get(pk=idUsuario))
    return render(request, 'puntuaciones_usuario.html', {'formulario':formulario, 'puntuaciones':puntuaciones, 'idUsuario':idUsuario, 'STATIC_URL':settings.STATIC_URL})
            