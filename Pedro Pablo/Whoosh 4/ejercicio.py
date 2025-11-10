#encoding:utf-8

from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID, DATETIME
from whoosh.qparser import QueryParser
import locale

PAGINAS = 1  #nÃºmero de pÃ¡ginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        crea_index()

# título, número de comensales, autor, fecha de actualización, características adicionales e introducción
def extraer_recetas():
    locale.setlocale(locale.LC_TIME, 'es_ES')
    resutados = []

    url = "https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f,"lxml")

    lista = s.find_all("a", class_="titulo titulo--resultado")
    enlaces = [i['href'] for i in lista]

    for enlace in enlaces:
        f = urllib.request.urlopen(enlace)
        s = BeautifulSoup(f,"lxml")
        titulo = s.find("h1", class_="titulo--articulo").get_text().strip()
        info = s.find("div", class_="recipe-info")
        if info:
            comensales = info.find("span").get_text().strip().replace(" comensales","").replace(" unidades","").replace(" comensal","")
        comautor = s.find("div", class_="nombre_autor")
        if comautor:
            autor = comautor.find("a").get_text().strip()
        actualizacion = s.find("span", class_="date_publish")
        if actualizacion:   
            fechaobtenida = actualizacion.get_text().replace("Actualizado: ","").strip()
            fecha = datetime.strptime(fechaobtenida, "%d %B %Y")
        caracteristicas = s.find("div", class_="properties inline").get_text().replace("Características adicionales:","").strip()
        if caracteristicas:
            caracteristicas = re.sub(r'\s*,\s*', ', ', caracteristicas).strip(' ,')
        introduccion = s.find("div", class_="intro")
        if introduccion:
            introduccion = introduccion.get_text().strip()

        resutados.append((titulo, comensales, autor, fecha, caracteristicas, introduccion))

    return resutados
        



def crea_index():
    sch = Schema(titulo=TEXT(stored=True), comensales=NUMERIC(stored=True, numtype=int), autor=ID(stored=True), fecha=DATETIME(stored=True), caracteristicas=KEYWORD(stored=True, commas=True), introduccion=TEXT)

    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    ix = create_in("Index", schema=sch)
    writer = ix.writer()

    i=0
    recetas= extraer_recetas()
    for r in recetas:
        writer.add_document(titulo=r[0], comensales=int(r[1]), autor=r[2], fecha=r[3], caracteristicas=r[4], introduccion=r[5])
        i+=1
    writer.commit()              
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " recetas")  


if __name__ == "__main__":
    cargar()