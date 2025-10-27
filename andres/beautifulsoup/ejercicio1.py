# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import Entry, Label, Spinbox, messagebox, Tk, Menu, Toplevel, Listbox, Scrollbar, RIGHT, LEFT, Y, BOTH, END
import sqlite3

# lineas para evitar error SSL
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://www.vinissimus.com/es/vinos/tinto/?cursor="


def store_data():
    conn = sqlite3.connect("vinos.db")
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS VINO")
    conn.execute("DROP TABLE IF EXISTS TIPOS_UVAS")
    conn.execute('''CREATE TABLE VINO
       (NOMBRE            TEXT NOT NULL,
        PRECIO            REAL,
        DENOMINACION      TEXT,
        BODEGA            TEXT,
        TIPO_UVAS         TEXT);''')
    conn.execute('''CREATE TABLE TIPOS_UVAS
       (NOMBRE            TEXT NOT NULL);''')

    list_wines = []
    types_grapes = set()

    for i in range(0, 3):
        url = BASE_URL + str(i*36)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        list_one_page = s.find_all("div", class_="product-list-item")
        list_wines.extend(list_one_page)

    for wine in list_wines:
        data = wine.find("div", class_="details")
        name = data.a.h2.string.strip()
        cellar = data.find("div", class_="cellar-name").string.strip()
        designation = data.find("div", class_="region").string.strip()
        grapes = "".join(data.find("div", class_="tags").stripped_strings)
        for grape in grapes.split("/"):
            types_grapes.add(grape.strip())
        price = list(wine.find("p", class_="price").stripped_strings)[0]
        discount = wine.find("p", class_="price").find_next_sibling("p", class_="dto")
        if discount:
            price = list(discount.stripped_strings)[0]

        conn.execute("""INSERT INTO VINO (NOMBRE, PRECIO, DENOMINACION, BODEGA, TIPO_UVAS) VALUES (?,?,?,?,?)""",
                     (name, float(price.replace(',', '.')), designation, cellar, grapes))

    conn.commit()

    for grape in list(types_grapes):
        conn.execute("""INSERT INTO TIPOS_UVAS (NOMBRE) VALUES (?)""", (grape,))

    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM VINO")
    cursor1 = conn.execute("SELECT COUNT(*) FROM TIPOS_UVAS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " vinos y "
                        + str(cursor1.fetchone()[0]) + " tipos de uvas")

    conn.close()


def load():
    response = messagebox.askyesno("Confirm", "This will reload the data. Do you want to continue?")
    if response:
        store_data()


def list_wines(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'VINO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = "     PRECIO: " + str(row[1]) + ' | BODEGA: ' + row[2] + ' | DENOMINACION: ' + row[3]
        lb.insert(END, s)
        lb.insert(END, "\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def list_all():
    conn = sqlite3.connect("vinos.db")
    conn.text_factory = str
    cursor = conn.execute("SELECT NOMBRE, PRECIO, BODEGA, DENOMINACION FROM VINO")
    list_wines(cursor)


def search_by_designation():
    def list(event):
        conn = sqlite3.connect("vinos.db")
        conn.text_factory = str
        cursor = conn.execute("SELECT NOMBRE, PRECIO, BODEGA, DENOMINACION FROM VINO WHERE DENOMINACION LIKE '%" + str(Entry.get()) + "%'")
        list_wines(cursor)

    conn = sqlite3.connect("vinos.db")
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT DENOMINACION FROM VINO")
    designations = [d[0] for d in cursor]

    v = Toplevel()
    lb = Label(v, text="Enter designation: ")
    lb.pack(side=LEFT)
    entry = Spinbox(v, width=50, values=designations)
    entry.bind("<Return>", list)
    entry.pack(side=LEFT)


def search_by_grape():
    return


def search_by_price():
    return


def main_window():
    root = Tk()
    root.title("Ejercicio 1 - BeautifulSoup")

    menu = Menu(root)

    menudata = Menu(menu, tearoff=0)
    menudata.add_command(label="Load", command=load)
    menudata.add_command(label="List", command=list_all)
    menudata.add_command(label="Exit", command=root.quit)
    menu.add_cascade(label="Data", menu=menudata)

    menusearch = Menu(menu, tearoff=0)
    menusearch.add_command(label="By designation", command=search_by_designation)
    menusearch.add_command(label="By grape", command=search_by_grape)
    menusearch.add_command(label="By price", command=search_by_price)
    menu.add_cascade(label="Search", menu=menusearch)

    root.config(menu=menu)
    root.mainloop()


if __name__ == "__main__":
    main_window()
