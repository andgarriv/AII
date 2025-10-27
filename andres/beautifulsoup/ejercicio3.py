#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import re

JORNADAS = 38

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extaer_datos():
    url = "http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, 'lxml')

    for jornada in range(1, JORNADAS + 1):
        l = s.find_all(id="jornada-" + str(jornada))
        print(l)
        
def almacenar_bd():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS JUEGOS") 
    conn.execute('''CREATE TABLE JUEGOS
       (TITULO        TEXT    NOT NULL,
       VOTOS          INT    ,
       PRECIO         FLOAT    ,
       TEMATICAS        TEXT    ,
       COMPLEJIDAD      TEXT);''')
    conn.close()

if __name__ == "__main__":
    extaer_datos()
    almacenar_bd()
