# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import Entry, Label, Spinbox, messagebox, Tk, Menu, Toplevel, Listbox, Scrollbar, RIGHT, LEFT, Y, BOTH, END
from tkinter import messagebox
import re

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_jornadas():
    f = urllib.request.urlopen("http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/")
    s = BeautifulSoup(f,"lxml")

    l = s.find_all("div", class_= ["cont-modulo","resultados"])
    return l


def ventana_principal():
    raiz = Tk()
    raiz.title("Ejercicio - BeautifulSoup")

    menu = Menu(raiz)

    raiz.config(menu=menu)
    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
