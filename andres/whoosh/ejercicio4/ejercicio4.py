#encoding:utf-8

from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID, DATETIME
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
import locale

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operaciÃ³n puede ser lenta")
    if respuesta:
        almacenar_datos()


def extraer_recetas():
    locale.setlocale(locale.LC_TIME, 'es_ES')
    lista_urls = []
    lista = []

    url = "https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")

    for a in s.find_all("a", class_="titulo titulo--resultado"):
        href = a.get("href")
        if href:
            lista_urls.append(href)

    for i in lista_urls:
        f = urllib.request.urlopen(i)
        s = BeautifulSoup(f, "lxml")

        titulo = s.find("h1", class_="titulo--articulo").string.strip()
        com_tag = s.find(attrs={"class": re.compile(r"\b(?:comensales|unidades)\b", re.I)})
        comensales = None
        if com_tag:
            m = re.search(r"\d+", com_tag.get_text())
            if m:
                comensales = int(m.group())
        autor_div = s.find("div", class_="nombre_autor")
        if autor_div:
            autor = autor_div.find("a").get_text().strip()
        fecha = s.find("span", class_="date_publish").get_text().replace("Actualizado:", "").strip()
        fecha = datetime.strptime(fecha, "%d %B %Y")
        caracteristicas = s.find("div", class_="properties inline").get_text().replace("Características adicionales:", "").strip()
        caracteristicas = re.sub(r'\s*,\s*', ', ', caracteristicas).strip(' ,')
        intro = s.find("div", class_="intro").get_text().strip()
        lista.append((titulo, comensales, autor, fecha, caracteristicas, intro))
    print(lista)
    return lista


def almacenar_datos():

    schem = Schema(titulo=TEXT(stored=True), comensales=NUMERIC(stored=True, numtype=int), autor=ID(stored=True), fecha=DATETIME(stored=True), caracteristicas=KEYWORD(stored=True,commas=True), introduccion=TEXT(stored=True))

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i=0
    lista = extraer_recetas()
    for receta in lista:
        writer.add_document(titulo=receta[0], comensales=str(receta[1]), autor=receta[2], fecha=receta[3], caracteristicas=receta[4], introduccion=receta[5])
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " recetas")


def buscar_titulo_introduccion():
    def mostrar_list(event):
        ix = open_dir("Index")
        with ix.searcher() as searcher:
            query = MultifieldParser(["titulo", "introduccion"]), ix.schema, group=OrGroup).parse(str(en.get()))
            results = searcher.search(query)
            v = Toplevel()
            v.title("Listado de Recetas")
            v.geometry("800x400")
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill=BOTH)

def ventana_principal():
    root = Tk()
    root.title("Indexador de recetas")
    root.geometry("1280x720")
    menubar = Menu(root)

    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_separator()
    datosmenu.add_command(label="Salir", command=root.quit)

    menubar.add_cascade(label="Datos", menu=datosmenu)

    buscarmenu = Menu(menubar, tearoff=0)
    # buscarmenu.add_command(label="Buscar", command=buscar_titulo_introduccion)

    menubar.add_cascade(label="Buscar", menu=buscarmenu)

    root.config(menu=menubar)
    root.mainloop()


if __name__ == "__main__":
    ventana_principal()
