#encoding:utf-8

from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from tkinter import messagebox
from tkinter import *
import re

BASE_URL = "https://www.imdb.com"

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context



def extraer_peliculas():
    
    main_url = "https://www.imdb.com/es-es/chart/top/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    f = urllib.request.urlopen(urllib.request.Request(main_url, headers=headers))
    s = BeautifulSoup(f, "lxml")
    l = s.find_all("a", class_="ipc-title-link-wrapper")
    resultado = [i['href'] for i in l]
    return resultado

def almacenar_bd():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS PELICULAS") 
    conn.execute('''CREATE TABLE PELICULAS
       (NOMBRE TEXT,
        ESTRENO INTEGER,
        DURACION TEXT,
        ACTORES TEXT,
        PUNTUACION REAL,
        GENERO TEXT);''')
    l = extraer_peliculas()
    for i in l:
        url = BASE_URL + i
        headers = {'User-Agent': 'Mozilla/5.0'}
        f = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        s = BeautifulSoup(f, "lxml")
        titulo = s.find("span", class_="hero__primary-text")
        if titulo:
            titulo = titulo.get_text().strip()
        div = s.find("div", class_="iOkLEK")
        if div:
            estreno = int(div.find("a", class_="ipc-link ipc-link--baseAlt ipc-link--inherit-color").get_text().strip())
        duracion = div.find_all("li", class_="ipc-inline-list__item")
        if duracion:
            duracion = duracion[-1].get_text().strip()
        actores = s.find_all("a", attrs={"data-testid":"title-cast-item__actor"})  
        if actores:
            actores = [i.string.strip() for i in actores]
        puntuacion = s.find("span", class_="sc-4dc495c1-1 lbQcRY")
        if puntuacion:
            puntuacion = float(puntuacion.string.strip().replace(',','.'))
        genero = s.find_all("a", class_="ipc-chip ipc-chip--on-baseAlt")
        if genero:
            genero = [i.get_text().strip() for i in genero]
                
        conn.execute("""INSERT INTO PELICULAS VALUES (?,?,?,?,?,?)""",(titulo,estreno,duracion,', '.join(actores),puntuacion,', '.join(genero)))
        
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM PELICULAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()



def ventana_principal():
    raiz = Tk()
    raiz.title("Ejercicio Invent - BeautifulSoup")

    menu = Menu(raiz)

    raiz.config(menu=menu)
    raiz.mainloop()


if __name__ == "__main__":
    almacenar_bd()
    