#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from tkinter import messagebox
from tkinter import *


# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operaciÃ³n puede ser lenta")
    if respuesta:
        almacenar_bd()

def extraer_juegos():
    listajuegos = []
    for num_paginas in range (0,2):
        url = "https://zacatrus.es/juegos-de-mesa.html?p=" + str(num_paginas)
        f = urllib.request.urlopen(url)
        objetos = BeautifulSoup(f, 'html.parser')
        listar_una_pagina = objetos.find_all("li", class_="product-item")
        listajuegos.extend(listar_una_pagina)

if __name__ == "__main__":
    extraer_juegos()
