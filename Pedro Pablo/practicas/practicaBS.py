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


BASE_URL = "https://editorialamarante.es"
TOP_URL = "/libros/narrativa"


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_bd()


def extraer_libros():
    url = "https://editorialamarante.es/libros/narrativa"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    lista = s.find_all("a", class_="book-link")
    resultado = [i['href'] for i in lista]
    return resultado


def almacenar_bd():
    conn = sqlite3.connect('libros.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS LIBROS")
    conn.execute('''CREATE TABLE LIBROS
        (TITULO       TEXT NOT NULL,
        GENEROS          TEXT    NOT NULL,
        FECHA      TEXT    NOT NULL,
        PRECIO        REAL    NOT NULL,
        AUTOR        TEXT NOT NULL,
        URL_AUTOR           TEXT NOT NULL);''')

    lista_urls = extraer_libros()
    for url in lista_urls:
        f = urllib.request.urlopen(BASE_URL + url)
        s = BeautifulSoup(f, "lxml")
        titulo = s.find("h2", attrs={"itemprop": "name"})
        if titulo:
            titulo = titulo.get_text().strip()
        genero = s.find("span", attrs={"itemprop": "genre"})
        if genero:
            genero = genero.get_text().strip()
        fecha = s.find("meta", attrs={"itemprop": "datePublished"})
        if fecha:
            fecha = fecha['content'].strip()
        precio = None
        div = s.find("div", class_="col-md-5")
        if div:
            texto = div.get_text()
            match = re.search(r"Precio:\s*(\d+(?:\.\d+)?)\s*€", texto)
            if match:
                precio = float(match.group(1))
        autor = s.find("a", attrs={"itemprop": "author"})
        if autor:
            autor_nombre = autor.get_text().strip()
            autor_url = autor['href'].strip()
        conn.execute("""INSERT INTO LIBROS (TITULO, GENEROS, FECHA, PRECIO, AUTOR, URL_AUTOR) VALUES (?,?,?,?,?,?)""",
                     (titulo, genero, fecha, precio, autor_nombre, autor_url))

    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM LIBROS")
    messagebox.showinfo("Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_libros():
    conn = sqlite3.connect('libros.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT TITULO, GENEROS, FECHA,PRECIO,AUTOR, URL_AUTOR FROM LIBROS")
    conn.close
    listar_libros_detallado(cursor, titulo="Listado de libros")


def listar_libros_mas_baratos():
    conn = sqlite3.connect('libros.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT TITULO, GENEROS, FECHA, PRECIO, AUTOR, URL_AUTOR FROM LIBROS ORDER BY PRECIO ASC LIMIT 5")
    conn.close
    listar_libros_detallado(cursor, titulo="Libros más baratos")


def buscar_por_genero():
    def listar(event):
        conn = sqlite3.connect('libros.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT TITULO, GENEROS, FECHA, PRECIO, AUTOR, URL_AUTOR FROM LIBROS where GENEROS LIKE '%" + str(entry.get())+"%'")
        conn.close
        listar_libros_detallado(cursor, titulo="Listado de libros por género")

    conn = sqlite3.connect('libros.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT GENEROS FROM LIBROS")

    generos = set()
    for i in cursor:
        generos_LIBROS = i[0].split(".")
        for genero in generos_LIBROS:
            generos.add(genero.strip())

    v = Toplevel()
    label = Label(v, text="Seleccione un genero ")
    label.pack(side=LEFT)
    entry = Spinbox(v, values=list(generos), state='readonly')
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

    conn.close()


def buscar_por_autor():
    def listar(event):
        conn = sqlite3.connect('libros.db')
        conn.text_factory = str
        try:
            nombre = en.get()
            cur = conn.execute("SELECT URL_AUTOR FROM LIBROS WHERE AUTOR LIKE '%" + str(nombre) + "%'")
            fila = cur.fetchone()
            if not fila or not fila[0]:
                conn.close()
                messagebox.showerror("Autor", "No se encontró la página del autor en la BD.")
                return
            url_autor = fila[0]
            conn.close()

            f = urllib.request.urlopen(BASE_URL + url_autor)
            s = BeautifulSoup(f, "lxml")

            a_twitter = s.find("a", class_="share-twitter")
            twitter = a_twitter['href'].strip() if a_twitter and a_twitter.has_attr('href') else "No encontrado"

            ul = s.find("ul", id="author-list-books")
            if ul:
                n_libros = len(ul.find_all("li"))
            else:
                n_libros = 0

            v = Toplevel()
            v.title("Datos de autor")
            texto = "AUTOR: " + nombre + "\n\n" + "Twitter: " + twitter + "\n" + "Libros publicados: " + str(n_libros)
            lb = Label(v, text=texto)
            lb.pack()

        except:
            try:
                conn.close()
            except:
                pass
            messagebox.showerror("Error", "No se pudieron obtener los datos del autor.")
            return

    conn = sqlite3.connect('libros.db')
    conn.text_factory = str
    cur = conn.execute("SELECT DISTINCT AUTOR FROM LIBROS")
    autores = [i[0] for i in cur]
    conn.close()

    if not autores:
        messagebox.showinfo("Autor", "No hay autores en la base de datos.")
        return

    v = Toplevel()
    lb = Label(v, text="Seleccione autor: ")
    lb.pack(side=LEFT)
    en = Spinbox(v, values=autores, state="readonly")
    en.bind("<Return>", listar)
    en.pack(side=LEFT)


def buscar_por_fecha():
    def listar(event):
        conn = sqlite3.connect('libros.db')
        conn.text_factory = str
        try:
            fecha_input = str(entry.get()).strip()
            fecha_dt = datetime.strptime(fecha_input, "%d/%m/%Y")
            fecha_iso = datetime.strftime(fecha_dt, "%Y-%m-%d")
            cursor = conn.execute(
                "SELECT TITULO, GENEROS, FECHA, PRECIO, AUTOR, URL_AUTOR FROM LIBROS WHERE FECHA > ? ORDER BY FECHA",
                (fecha_iso,)
            )
            listar_libros_detallado(cursor, titulo="Libros publicados en " + fecha_input)
        except:
            messagebox.showerror(title="Error", message="Error en la fecha\nFormato dd/mm/aaaa")

    v = Toplevel()
    label = Label(v, text="Introduzca la fecha (dd/mm/aaaa) ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)


def listar_libros_detallado(cursor, titulo):
    v = Toplevel()
    v.title(titulo)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)

    for row in cursor:
        lb.insert(END, "TÍTULO: " + str(row[0]))
        lb.insert(END, "-----------------------------------------------------")
        lb.insert(END, "     GÉNERO/S: " + str(row[1]))
        lb.insert(END, "     FECHA DE PUBLICACIÓN: " + str(row[2]))
        lb.insert(END, "     PRECIO: " + str(row[3]) + " €")
        lb.insert(END, "     AUTOR: " + str(row[4]))
        lb.insert(END, "\n")

    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def ventana_principal():

    raiz = Tk()

    menu = Menu(raiz)

    # DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    # LISTAR

    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Libros", command=listar_libros)
    menudatos.add_command(label="Libros más baratos", command=listar_libros_mas_baratos)
    menu.add_cascade(label="Listar", menu=menudatos)

    # BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Libros por Género", command=buscar_por_genero)
    menubuscar.add_command(label="Libros por Fecha", command=buscar_por_fecha)
    menubuscar.add_command(label="Datos de autor", command=buscar_por_autor)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
