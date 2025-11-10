# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import Tk, Menu
from tkinter import messagebox
import locale
import shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.qparser import QueryParser,

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_datos()


def almacenar_datos():

    schem = Schema(
        titulo=TEXT(stored=True),
        fecha=DATETIME(stored=True),
        autor=ID(stored=True),
        resumen=TEXT,
        enlace_detalles=ID
    )

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i = 0
    lista = extraer_noticias()
    for noticia in lista:
        writer.add_document(
            titulo=str(noticia[0]),
            fecha=noticia[1],
            autor=str(noticia[2]),
            resumen=str(noticia[3]),
            enlace_detalles=str(noticia[4])
        )
        i += 1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i) + " noticias")
    return


def extraer_noticias():
    locale.setlocale(locale.LC_TIME, 'es_ES')
    lista = []

    url = "https://muzikalia.com/category/noticia/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")

    for div in s.find_all("div", class_="cm-post-content"):
        titulo = div.find("h2", class_="cm-entry-title").get_text().strip()
        fecha = div.find("time", class_="entry-date").get_text().strip()
        fecha = datetime.strptime(fecha, "%d %B, %Y")
        resumen = div.find("div", class_="cm-entry-summary").find("p").get_text().strip()
        autor = div.find("span", class_="cm-author").get_text().strip()
        enlace_detalles = div.find("a", class_="cm-entry-button").get("href")

        lista.append((titulo, fecha, resumen, autor, enlace_detalles))

    return lista


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

    root.config(menu=menubar)
    root.mainloop()


if __name__ == "__main__":
    ventana_principal()
