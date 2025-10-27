# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import Entry, Label, Spinbox, messagebox, Tk, Menu, Toplevel, Listbox, Scrollbar, RIGHT, LEFT, Y, BOTH, END
from datetime import datetime
import re
import sqlite3

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

PAGINAS = 2  # número de páginas


def extraer_juegos():
    lista=[]

    for p in range(1,PAGINAS+1):
        url="https://zacatrus.es/juegos-de-mesa.html?p="+str(p)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f,"lxml")      

        l = s.ol.find_all("div", class_= "product-item-details")

        for i in l:
            titulo = i.a.string.strip()
            votos = i.find("div",class_="rating-result")
            if votos:
                votos = int(re.compile(r'\d+').search(votos['title']).group())
            else:
                votos = -1
            precio = re.compile(r'\d+,\d+').search(i.find("span", class_="price").string.strip()).group()
            precio = float(precio.replace(',','.'))

            f1 = urllib.request.urlopen(i.a['href'])
            j = BeautifulSoup(f1,"lxml")

            t = j.find("div", class_="data table additional-attributes")       
            if t :#tienen alguna/s de las caracterÃ­sticas adicionales
                tematica = t.find("div",attrs={"data-th":"TemÃ¡tica"})
                if tematica:
                    tematica = tematica.string.strip()
                else:
                    tematica = "Desconocida"
                complejidad = t.find("div",attrs={"data-th":"Complejidad"})
                if complejidad:
                    complejidad = complejidad.string.strip()
                else:
                    complejidad = "Desconocida"
            else:
                # no tienen características adicionales
                tematica = "Desconocida"
                complejidad = "Desconocida"
            t = j.find("div", class_="product attribute description")
            detalles = ""
            if t:
                detalles = t.get_text(separator="\n", strip=True)
            jugadores = t.find("div", attrs={"data-th": "Núm. jugadores"})
            if jugadores:
                jugadores = jugadores.string.strip()
            else:
                jugadores = "Desconocido"
            lista.append((titulo, votos, precio, tematica, complejidad, detalles, jugadores))

    return lista


def ventana_principal():
    ventana = Tk()
    ventana.title("Ejercicio 2 Whoosh")
    ventana.geometry("400x200")

    menu_bar = Menu(ventana)
    archivo_menu = Menu(menu_bar, tearoff=0)
    archivo_menu.add_command(label="Salir", command=ventana.quit)
    menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

    accion_menu = Menu(menu_bar, tearoff=0)
    accion_menu.add_command(label="Cargar datos", command=cargar)
    menu_bar.add_cascade(label="Acción", menu=accion_menu)

    ventana.config(menu=menu_bar)
    ventana.mainloop()


if __name__ == "__main__":
    extraer_juegos()
