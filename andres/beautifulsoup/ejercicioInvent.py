# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import Entry, Label, Spinbox, messagebox, Tk, Menu, Toplevel, Listbox, Scrollbar, RIGHT, LEFT, Y, BOTH, END
import sqlite3
import re

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://www.imdb.com"
TOP_URL = "/es-es/chart/top/"


def extraer_peliculas():
    url = BASE_URL + TOP_URL
    list_urls = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    f = urllib.request.urlopen(req)
    s = BeautifulSoup(f, "lxml")
    links = s.find_all("a", class_="ipc-title-link-wrapper")
    list_urls = [a['href'] for a in links]
    return list_urls


def almacenar_bd(db_path='peliculas.db'):
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS PELICULAS")
    conn.execute('''CREATE TABLE PELICULAS
       (NOMBRE TEXT
        ESTRENO INTEGER
        DURACION TEXT
        ACTORES TEXT
        PUNTUACION REAL
        GENERO TEXT);''')
    conn.commit()

    resultados = extraer_peliculas()

    for i in resultados:
        url = BASE_URL + i
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, "lxml")
        nombre = s.find("span", class_="hero__primary-text").string.strip()
        estreno = next((int(a.text.strip()) for a in s.find_all("a", class_="ipc-link ipc-link--baseAlt ipc-link--inherit-color") if a.text.strip().isdigit() and len(a.text.strip()) == 4), None)
        puntuacion = next((float(span.text.strip().replace(',', '.')) for span in s.find_all("span", class_="sc-4dc495c1-1 lbQcRY") if re.match(r"^\d+([.,]\d+)?$", span.text.strip())), None)
        actores = [a.string.strip() for a in s.find_all("a", attrs={"data-testid": "title-cast-item__actor"})]
        print(puntuacion)

    try:
        for r in resultados:
            try:
                conn.execute("""INSERT OR IGNORE INTO PELICULAS
                                (NOMBRE, ESTRENO, DURACION, ACTORES, PUNTUACION, GENERO)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""", r)
            except Exception as e:
                print("Error insertando:", e, r)
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM PELICULAS").fetchone()[0]
        messagebox.showinfo("Base Datos", f"Base de datos creada correctamente\nHay {total} registros")
    finally:
        conn.close()


def ventana_principal():
    raiz = Tk()
    raiz.title("Ejercicio Invent - BeautifulSoup")

    menu = Menu(raiz)

    raiz.config(menu=menu)
    raiz.mainloop()


if __name__ == "__main__":
    almacenar_bd()
    # ventana_principal()
