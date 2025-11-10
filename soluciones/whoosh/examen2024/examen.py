# encoding:utf-8
"""
Examen Whoosh

Fecha: 12/11/2024
"""
from tkinter import *
from tkinter import messagebox
import urllib.request
import os, ssl, shutil, re
from bs4 import BeautifulSoup
from datetime import datetime
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
import locale
from whoosh.sorting import Facets, FieldFacet
from whoosh.query import And, Not
from datetime import datetime, time


if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context


def ventana_principal():
    raiz = Tk()
    raiz.title("Examen Whoosh")
    raiz.geometry("1600x800")
    raiz.configure(bg="orange")
    fuente = Label(
        raiz,
        text="https://sevilla.cosasdecome.es/eventos/filtrar?pg=1 ",
        bg="orange",
        font=("Arial", 15),
    )
    fuente.pack(side=TOP, fill=BOTH)
    info = Label(
        raiz,
        text="Examen Whoosh",
        bg="orange",
        font=("Arial", 12),
    )
    info.pack(side=BOTTOM, fill=BOTH)

    menu = Menu(raiz)

    # Datos
    menudatos = Menu(menu, tearoff=0)
    menu.add_cascade(label="Datos", menu=menudatos)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar)
    menudatos.add_command(label="Salir", command=raiz.quit)

    # Buscar
    menubuscar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Buscar y Modificar", menu=menubuscar)
    menubuscar.add_command(label="Eventos por población", command=eventos_por_poblacion)
    menubuscar.add_command(label="Categoría y Descripción", command=buscar_categoria_descripcion)
    menubuscar.add_command(label="Fecha y Título", command=buscar_fecha_y_titulo)
    menubuscar.add_command(label="Modificar las fechas", command=modificar_fechas)
    menubuscar.add_command(label="Eventos que se celebran por la noche", command=eventos_noche)

    raiz.config(menu=menu)

    raiz.mainloop()


def cargar():
    respuesta = messagebox.askyesno(
        title="Cargar",
        message="¿Desea cargar los datos? Esta operación puede ser lenta.",
        icon="question",
    )
    if respuesta:
        almacenar_datos()


def extraer_datos():
    lista = []

    for p in range(1, 4):
        req = urllib.request.Request(
            "https://sevilla.cosasdecome.es/eventos/filtrar?pg=" + str(p),
            headers={"User-Agent": "Mozilla/5.0"},
        )
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, "lxml")

        l = s.find_all("div", class_="post-details")

        for i in l:
            titulo = i.a.string.strip()

            req1 = urllib.request.Request(
                i.a["href"], headers={"User-Agent": "Mozilla/5.0"}
            )
            f1 = urllib.request.urlopen(req1)
            s1 = BeautifulSoup(f1, "lxml")
            l1 = s1.find("section", class_="post-content")

            lugar = l1.find("div", class_="block-elto lugar")
            if lugar:
                lugar = "".join(lugar.find("div", class_="value").p.stripped_strings)
            else:
                lugar = "Desconocido"

            poblacion = l1.find("div", class_="block-elto poblacion")
            if poblacion:
                poblacion = poblacion.find("div", class_="value").a.string.strip()
            else:
                poblacion = "Desconocido"

            fechas = l1.find("div", class_="block-elto fechas")
            if fechas:
                fechas = fechas.i.next_sibling.strip()
                fechas = re.findall(r"\d{2}/\d{2}/\d{4}", fechas)
                fecha_inicio = fechas[0]
                if len(fechas) > 1:
                    fecha_fin = fechas[1]
                else:
                    fecha_fin = fecha_inicio
            else:
                fecha_inicio = None
                fecha_fin = None

            hora = l1.find("div", class_="block-elto hora")
            if hora:
                hora = list(hora.find("div", class_="value").strings)[1].strip()
            else:
                hora = "Desconocido"

            categorias = l1.find("div", class_="block-elto categoria")
            if categorias:
                cat = categorias.find_all("div", class_="value")
                categorias = cat[0].a.string.strip()
                for i in range(1, len(cat)):
                    categorias = categorias + "," + cat[i].a.string.strip()
            else:
                categorias = "Desconocido"

            descripcion = l1.find("div", class_="block-elto descripcion")
            if descripcion:
                descripcion = descripcion.find("div", class_="value").text.strip()
            else:
                descripcion = "Desconocido"

            lista.append(
                (
                    titulo,
                    lugar,
                    poblacion,
                    fecha_inicio,
                    fecha_fin,
                    hora,
                    categorias,
                    descripcion,
                )
            )

    return lista


def almacenar_datos():
    lista = extraer_datos()
    schem = Schema(
        id = ID(stored=True, unique=True),
        titulo=TEXT(stored=True, phrase=False),
        lugar=TEXT(stored=True, phrase=False),
        poblacion=TEXT(stored=True, phrase=False),
        fecha_inicio=DATETIME(stored=True),
        fecha_fin=DATETIME(stored=True),
        hora=TEXT(stored=True, phrase=False),
        categoria=KEYWORD(stored=True, commas=True, lowercase=True),
        descripcion=TEXT(stored=True, phrase=True),
    )

    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema=schem)
    writer = ix.writer()
    i = 0
    
    for evento in lista:
        try:
            
            writer.add_document(
                id=str(i),
                titulo=evento[0],
                lugar=evento[1],
                poblacion=evento[2],
                fecha_inicio=datetime.strptime(evento[3], "%d/%m/%Y"),
                fecha_fin=datetime.strptime(evento[4], "%d/%m/%Y"),
                hora=evento[5],
                categoria=evento[6],
                descripcion=evento[7],
            )
            i += 1
        except ValueError as e:
            print(e)
            print(evento)
        

        
    writer.commit()
    messagebox.showinfo(
        title="Cargar",
        message="Se han cargado " + str(i) + " eventos.",
        icon="info",
    )

def listar():
    ix = open_dir("index")
    with ix.searcher() as searcher:
        query = QueryParser("titulo", ix.schema).parse("*")
        results = searcher.search(query, limit=None)
        v = Toplevel()
        v.title("Listado de eventos")
        v.geometry("800x600")
        v.configure(bg="orange")
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, yscrollcommand=sc.set)
        lb.pack(side=TOP, fill=BOTH, expand=True)
        sc.config(command=lb.yview)
        
        for r in results:
            lb.insert(END, "-" * 80)
            lb.insert(END, f"Título: {r['titulo']}")
            lb.insert(END, f"Población: {r['poblacion']}")
            lb.insert(END, f"Fecha inicio: {r['fecha_inicio']}")
            lb.insert(END, f"Fecha fin: {r['fecha_fin']}")
            lb.insert(END, f"Hora: {r['hora']}")
            lb.insert(END, f"Categorías: {r['categoria']}")
            
def buscar_fecha_y_titulo():
    def mostrar_lista(event):
        ix = open_dir("index")
        with ix.searcher() as searcher:
            query1 = QueryParser("fecha_inicio", ix.schema).parse(e1.get())
            query2 = QueryParser("titulo", ix.schema).parse(e2.get())
            results = searcher.search(And([query1, query2]), limit=None)
            v = Toplevel()
            v.title("Listado de eventos")
            v.geometry("800x600")
            v.configure(bg="orange")
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=TOP, fill=BOTH, expand=True)
            sc.config(command=lb.yview)
            
            for r in results:
                lb.insert(END, "-" * 80)
                lb.insert(END, f"Título: {r['titulo']}")
                lb.insert(END, f"Población: {r['poblacion']}")
                lb.insert(END, f"Fecha inicio: {r['fecha_inicio']}")
                lb.insert(END, f"Fecha fin: {r['fecha_fin']}")
                lb.insert(END, f"Hora: {r['hora']}")
                
                lb.insert(END, f"Categorías: {r['categoria']}")
    
    v = Toplevel()
    v.title("Buscar por fecha y título")
    l1 = Label(v, text="Fecha (aaaammdd):")
    l1.pack(side=TOP)
    e1 = Entry(v)
    e1.pack(side=TOP)
    l2 = Label(v, text="Título:")
    l2.pack(side=TOP)
    e2 = Entry(v)
    e2.pack(side=TOP)
    b = Button(v, text="Buscar")
    b.pack(side=TOP)
    b.bind("<Button-1>", mostrar_lista)
    
def modificar_fechas():
    def modificar(event):
        ix = open_dir("index")
        with ix.searcher() as searcher:
            query = QueryParser("fecha_inicio", ix.schema).parse(e1.get())
            results = searcher.search(query, limit=None)

            respuesta = messagebox.askyesno(
                title="Modificar",
                message="Se han encontrado " + str(len(results)) + " eventos. ¿Desea modificar las fechas?",
                icon="question",
            )
            if respuesta:
                writer = ix.writer()
                nueva_fecha = datetime.strptime(e2.get(), "%Y%m%d")
                for r in results:
                    writer.update_document(
                        id=r["id"],
                        titulo=r["titulo"],
                        lugar=r["lugar"],
                        poblacion=r["poblacion"],
                        fecha_inicio=nueva_fecha,
                        fecha_fin=r["fecha_fin"],
                        hora=r["hora"],
                        categoria=r["categoria"],
                        descripcion=r["descripcion"],
                    )
                writer.commit()
                messagebox.showinfo(
                    title="Modificar",
                    message="Se han modificado " + str(len(results)) + " eventos.",
                    icon="info",
                )
    
    v = Toplevel()
    v.title("Modificar fechas")
    l1 = Label(v, text="Fecha (aaaammdd):")
    l1.pack(side=TOP)
    e1 = Entry(v)
    e1.pack(side=TOP)
    l2 = Label(v, text="Nueva fecha (aaaammdd):")
    l2.pack(side=TOP)
    e2 = Entry(v)
    e2.pack(side=TOP)
    b = Button(v, text="Modificar")
    b.pack(side=TOP)
    b.bind("<Button-1>", modificar)
    
def buscar_categoria_descripcion():
    def buscar():
        ix = open_dir("index")
        with ix.searcher() as searcher:
            categoria = spinbox.get()
            frase = entrada.get()
            try:
                query_categoria = QueryParser("categoria", ix.schema).parse(categoria)
                query_descripcion = Not(QueryParser("descripcion", ix.schema).parse(frase))
                query = And([query_categoria, query_descripcion])
                
                results = searcher.search(query, limit=3)
                ventana_resultados = Toplevel()
                ventana_resultados.title("Resultados de Búsqueda")
                ventana_resultados.geometry("800x600")
                ventana_resultados.configure(bg="lightblue")

                lista = Listbox(ventana_resultados, width=100, yscrollcommand=lambda f, l: sc.set(f, l))
                lista.pack(side=LEFT, fill=BOTH, expand=True)

                sc = Scrollbar(ventana_resultados, orient=VERTICAL, command=lista.yview)
                sc.pack(side=RIGHT, fill=Y)

                lista.delete(0, END)
                for r in results:
                    lista.insert(END, "-" * 80)
                    lista.insert(END, f"Título: {r['titulo']}")
                    lista.insert(END, f"Población: {r['poblacion']}")
                    lista.insert(END, f"Categorías: {r['categoria']}")
                    lista.insert(END, f"Descripción: {r['descripcion']}")
            except Exception as e:
                print(f"Error al ejecutar la búsqueda: {e}")
                
    ventana = Toplevel()
    ventana.title("Buscar por Categoría y Descripción")
    ventana.geometry("800x600")

    fuente = Label(
        ventana,
        text="Buscar por Categoría y Descripción"
    )
    fuente.pack(side=TOP, fill=BOTH)

    ix = open_dir("index")
    with ix.searcher() as searcher:
        categorias = set()
        for r in searcher.documents():
            categorias.update(r['categoria'].split(','))

    spinbox = Spinbox(ventana, values=tuple(categorias), width=50)
    spinbox.pack(side=TOP, fill=BOTH)

    entrada = Entry(ventana, width=50)
    entrada.pack(side=TOP, fill=BOTH)

    boton = Button(ventana, text="Buscar", command=buscar)
    boton.pack(side=TOP, fill=BOTH)

    
def eventos_noche():
    ix = open_dir("index")
    with ix.searcher() as searcher:
        results = []
        for r in searcher.documents():
            if r.get("hora"):
                horas = re.findall(r"\d{2}:\d{2}", r["hora"])
                if horas:
                    # Consideramos que los eventos de noche son aquellos que empiezan a partir de las 20:00h
                    hora_inicio = datetime.strptime(horas[0], "%H:%M").time() 
                    if hora_inicio >= time(20, 0):
                        results.append(r)

        v = Toplevel()
        v.title("Eventos que se celebran por la noche")
        v.geometry("800x600")
        v.configure(bg="orange")
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, yscrollcommand=sc.set, font=("Arial", 12))
        lb.pack(side=TOP, fill=BOTH, expand=True)
        sc.config(command=lb.yview)

        for r in results:
            lb.insert(END, "-" * 80)
            lb.insert(END, f"Título: {r['titulo']}")
            lb.insert(END, f"Lugar: {r['lugar']}")
            lb.insert(END, f"Hora: {r['hora']}")
            lb.insert(END, "")
    

def cargar_poblaciones_desde_schema():
    lista_poblaciones = []
    try:
        ix = open_dir("index")
        with ix.searcher() as searcher:
            poblaciones_unicas = set()

            for doc in searcher.documents():
                if "poblacion" in doc:
                    poblaciones_unicas.add(doc["poblacion"].strip())

            lista_poblaciones = sorted(list(poblaciones_unicas))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar las poblaciones: {e}")
    return lista_poblaciones

def eventos_por_poblacion():
    def mostrar_eventos(event):
        ix = open_dir("index")
        with ix.searcher() as searcher:
            poblacion = spinbox.get()
            poblacion_query = QueryParser("poblacion", ix.schema).parse(poblacion)

            results = searcher.search(poblacion_query, limit=10)
            v = Toplevel()
            v.title(f"Eventos en {poblacion}")
            v.geometry("800x600")
            v.configure(bg="orange")
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set, font=("Arial", 12))
            lb.pack(side=TOP, fill=BOTH, expand=True)
            sc.config(command=lb.yview)
            for r in results:
                lb.insert(END, "-" * 80)
                lb.insert(END, f"Título: {r['titulo']}")
                lb.insert(END, f"Población: {r['poblacion']}")
                lb.insert(END, f"Fecha Inicio: {r['fecha_inicio']}")
                lb.insert(END, f"Fecha Fin: {r['fecha_fin']}")
                lb.insert(END, f"Hora: {r['hora']}")
                lb.insert(END, f"Categorías: {r['categoria']}")
                lb.insert(END, "")

    v = Toplevel()
    v.title("Buscar eventos por población")
    v.geometry("400x200")
    l1 = Label(v, text="Seleccione una población:")
    l1.pack(side=TOP, fill=X)
    lista_poblaciones = cargar_poblaciones_desde_schema()
    spinbox = Spinbox(v, values=lista_poblaciones)
    spinbox.pack(side=TOP, fill=X)
    spinbox.bind("<Return>", mostrar_eventos)
    
    
    


if __name__ == "__main__":
    ventana_principal()
