#encoding:utf-8

from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID, DATETIME
from whoosh.qparser import QueryParser
import locale
from whoosh import index, query
from datetime import datetime, timedelta
from whoosh.query import And, DateRange, Term


PAGINAS = 3  #nÃºmero de pÃ¡ginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        crea_index()

#  titulo, lugar, poblacion, fecha_inicio, fecha_fin, hora, categorias, descripcion,

def extraer_menus():
    lista = []
    for p in range(1, PAGINAS + 1):
        url = "https://sevilla.cosasdecome.es/eventos/filtrar?pg=" + str(p)
        headers = {'User-Agent': 'Mozilla/5.0'}
        f = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        s = BeautifulSoup(f,"lxml")
        detalles = s.find_all("div", class_="post-details")
        if detalles:
            enlaces = [i.find("a")['href'] for i in detalles]
        for enlace in enlaces:
            headers = {'User-Agent': 'Mozilla/5.0'}
            f = urllib.request.urlopen(urllib.request.Request(enlace, headers=headers))
            s = BeautifulSoup(f,"lxml")
            titulo = s.find("div", class_="post-title")
            if titulo:
                titulo = titulo.get_text().strip()
            lugar = s.find("div", class_="lugar")
            if lugar:
                lugar = lugar.find("p").get_text().strip()
            poblacion = s.find("div", class_="poblacion")
            if poblacion:
                poblacion = poblacion.find("a").get_text().strip()
            
            fecha = s.find("div", class_="fechas")
            if fecha:
                fecha = fecha.get_text().strip()
            m = re.findall(r'\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}', fecha)

            if len(m) >= 2:
                inicio = datetime.strptime(m[0], '%d/%m/%Y')
                fin    = datetime.strptime(m[1], '%d/%m/%Y')
            elif len(m) == 1:
                inicio = datetime.strptime(m[0], '%d/%m/%Y')
                fin = inicio   # o fin = None
            else:
                inicio = fin = None
            hora = s.find("div", class_="hora")
            if hora:
                hora = hora.get_text().strip()
            else:
                hora = "Desconocida"
            categorias = s.find("div", class_="categoria")
            if categorias:
                categorias = categorias.find("a").get_text().strip()
            descripcion_tag = s.find("div", class_="descripcion")
            if descripcion_tag:
                partes = []

                # Recorremos párrafos y listas en orden
                for elem in descripcion_tag.find_all(["p", "ul", "ol"], recursive=True):
                    if elem.name == "p":
                        partes.append(elem.get_text(" ", strip=True))
                    elif elem.name == "ul":
                        for li in elem.find_all("li", recursive=False):
                            partes.append(f"   • {li.get_text(' ', strip=True)}")
                    elif elem.name == "ol":
                        for i, li in enumerate(elem.find_all("li", recursive=False), start=1):
                            partes.append(f"   {i}. {li.get_text(' ', strip=True)}")

                descripcion = "\n".join(partes)
            else:
                print("No hay descripción")

            lista.append((titulo, lugar, poblacion, inicio, fin, hora, categorias, descripcion))
    return lista


def crea_index():
    sch = Schema(titulo=TEXT(stored=True), lugar=TEXT(stored=True), poblacion=TEXT(stored=True), fecha_inicio=DATETIME(stored=True), fecha_fin=DATETIME(stored=True), hora=TEXT(stored=True), categorias=KEYWORD(stored=True, commas=True), descripcion=TEXT)

    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    ix = create_in("Index", schema=sch)
    writer = ix.writer()

    i=0
    menus= extraer_menus()
    for r in menus:
        writer.add_document(titulo=r[0], lugar=r[1], poblacion=r[2], fecha_inicio=r[3], fecha_fin=r[4], hora=r[5], categorias=r[6], descripcion=r[7])
        i+=1
    writer.commit()              
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " menus")  


def imprimir_lista_eventos(cursor):
    v = Toplevel()
    v.title("LISTA DE EVENTOS")

    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)

    lb = Listbox(v, width=150, yscrollcommand=sc.set)

    for row in cursor:
        # row puede ser Hit (dict-like)
        titulo = row.get('titulo', '')
        lugar = row.get('lugar', '')
        poblacion = row.get('poblacion', '')
       

        lb.insert(END, titulo or "—")
        lb.insert(END, f"    Lugar: {lugar or '—'}")
        lb.insert(END, f"    Población: {poblacion or '—'}")
    

    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
def listar():
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        results = searcher.search(query.Every(), limit=None)
        imprimir_lista_eventos(results)

def eventos_por_poblacion():
    def mostrar(event=None):
        pob = en.get().strip()
        if not pob:
            messagebox.showwarning("Aviso", "Introduzca una población.")
            return
        ix = open_dir("Index") 
        with ix.searcher() as searcher:
            qp = QueryParser("poblacion", ix.schema)
            q = qp.parse(f'"{pob}"')  # frase exacta
            results = searcher.search(q, limit=None)
            imprimir_lista_eventos(results)

    v = Toplevel()
    v.title("Eventos por población")
    Label(v, text="Población:").pack(side=LEFT, padx=4)
    en = Entry(v, width=40)
    en.pack(side=LEFT, padx=4)
    en.bind("<Return>", mostrar)
    Button(v, text="Buscar", command=mostrar).pack(side=LEFT, padx=4)

def buscar_categoria_descripcion():
    def ejecutar():
        ix = open_dir("Index")
        with ix.searcher() as searcher:
            cat = sp.get()         # categoría seleccionada en el Spinbox
            descripcion = '"' +en.get().strip()+ '"'

            # Query full-text para la descripción
            parser = QueryParser("descripcion", ix.schema)
            q_desc = parser.parse(descripcion) if descripcion else None

            # Term exacto para la categoría (campo 'categorias' en el índice)
            q_cat = query.Term("categorias", cat) if cat else None

            # Combinamos:
            if q_cat and q_desc:
                q = query.And([q_cat, q_desc])
            elif q_cat:
                q = q_cat
            elif q_desc:
                q = q_desc
            else:
                q = None

            if q is None:
                results = []
            else:
                results = searcher.search(q, limit=None)

            imprimir_lista_eventos(results)

    v = Toplevel()
    v.title("Categoría y Descripción")
    Label(v, text="Categoría:").pack(side=LEFT, padx=4)

    ix = open_dir("Index")
    with ix.searcher() as searcher:
        categorias = sorted([
            (i.decode('utf-8', 'ignore') if isinstance(i, bytes) else str(i))
            for i in searcher.lexicon('categorias')
        ])
    sp = Spinbox(v, values=categorias, state="readonly", width=40)
    sp.pack(side=LEFT, padx=4)

    Label(v, text="Descripción (palabras):").pack(side=LEFT, padx=4)
    en = Entry(v, width=45)
    en.pack(side=LEFT, padx=4)
    Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=4)

def eventos_noche():
   
    def hhmm_a_minutos(hhmm):
        """Convierte 'HH:MM' a minutos totales desde medianoche."""
        if not re.match(r"^\d{2}:\d{2}$", hhmm):
            return None  # formato incorrecto
        h, m = hhmm.split(":")
        try:
            return int(h) * 60 + int(m)
        except:
            return None

    ix = open_dir("Index")
    with ix.searcher() as searcher:

        # Obtener todos los eventos
        todos = searcher.search(query.Every(), limit=None)

        nocturnos = []
        for h in todos:
            hora_txt = h.get("hora", "").strip()

            # Validar formato HH:MM
            minutos = hhmm_a_minutos(hora_txt)
            if minutos is None:
                continue  # Saltamos eventos sin hora válida

            # Condición nocturna
            if minutos >= 12*60 or minutos <= 6*60:
                nocturnos.append(h)

        # Mostrar resultados
        if not nocturnos:
            messagebox.showinfo("Info", "No hay eventos nocturnos.")
        else:
            imprimir_lista_eventos(nocturnos)

# def buscar_titulo_y_fecha_inicio():
  
#     def ejecutar(event=None):
#         fecha_txt = e_fecha.get().strip()
#         titulo_pal = e_titulo.get().strip()

#         if not titulo_pal:
#             messagebox.showwarning("Aviso", "Debe escribir palabras del título.")
#             return

#         # Validar fecha
#         try:
#             fecha_dt = datetime.strptime(fecha_txt, "%Y/%m/%d")
#         except ValueError:
#             messagebox.showerror("ERROR", "Formato de fecha incorrecto. Use YYYY/MM/DD.")
#             return

#         ix = open_dir("Index")
#         with ix.searcher() as searcher:
#             parser_titulo = QueryParser("titulo", ix.schema)
#             q_titulo = parser_titulo.parse(titulo_pal)

#             # Consulta por fecha exacta (mismo día)
#             fecha_inicio = fecha_dt
#             fecha_fin = fecha_dt + timedelta(days=1)
#             q_fecha = DateRange("fecha_inicio", fecha_inicio, fecha_fin, startexcl=False, endexcl=True)

#             q_final = And([q_titulo, q_fecha])
#             results = searcher.search(q_final, limit=None)

#             imprimir_lista_eventos(results)

#     # --- Ventana de búsqueda ---
#     v = Toplevel()
#     v.title("Buscar por Título y Fecha de Inicio")

#     Label(v, text="Fecha inicio (YYYY/MM/DD):").pack(side=LEFT, padx=4)
#     e_fecha = Entry(v, width=12)
#     e_fecha.pack(side=LEFT, padx=4)
#     e_fecha.bind("<Return>", ejecutar)

#     Label(v, text="Título (palabras):").pack(side=LEFT, padx=4)
#     e_titulo = Entry(v, width=40)
#     e_titulo.pack(side=LEFT, padx=4)
#     e_titulo.bind("<Return>", ejecutar)

#     Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=6)

def buscar_titulo_y_fecha_inicio():
  
    def ejecutar(event=None):
        fecha_txt = e_fecha.get().strip()
        titulo_pal = e_titulo.get().strip()

        if not titulo_pal:
            messagebox.showwarning("Aviso", "Debe escribir palabras del título.")
            return

        # Validar formato de fecha: YYYY/MM/DD
        if not re.match(r"^\d{4}/\d{2}/\d{2}$", fecha_txt):
            messagebox.showerror("ERROR", "Formato de fecha incorrecto. Use YYYY/MM/DD.")
            return

        try:
            fecha_txt = datetime.strptime(fecha_txt, "%Y/%m/%d")
            print(fecha_txt)
        except ValueError:
            messagebox.showerror("ERROR", "Fecha no válida.")
            return

        ix = open_dir("Index")
        with ix.searcher() as searcher:
            # Buscar por título (usa parser sin OrGroup → comportamiento AND)
            parser_titulo = QueryParser("titulo", ix.schema)
            q_titulo = parser_titulo.parse(titulo_pal)

            # Buscar por fecha exacta (texto literal)
            q_fecha = query.Term("fecha_inicio", fecha_txt)

            # Combinar ambas condiciones (titulo + fecha_inicio)
            q_final = query.And([q_titulo, q_fecha])

            results = searcher.search(q_final, limit=None)
            imprimir_lista_eventos(results)

    # --- Ventana de búsqueda ---
    v = Toplevel()
    v.title("Buscar por Título y Fecha de Inicio")

    Label(v, text="Fecha inicio (YYYY/MM/DD):").pack(side=LEFT, padx=4)
    e_fecha = Entry(v, width=12)
    e_fecha.pack(side=LEFT, padx=4)
    e_fecha.bind("<Return>", ejecutar)

    Label(v, text="Título (palabras):").pack(side=LEFT, padx=4)
    e_titulo = Entry(v, width=40)
    e_titulo.pack(side=LEFT, padx=4)
    e_titulo.bind("<Return>", ejecutar)

    Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=6)

def ventana_principal():
    raiz = Tk()
    raiz.geometry("350x140")
    raiz.title("Eventos (Scraping + Whoosh)")

    menu = Menu(raiz)

    # Datos
    menudatos = Menu(menu, tearoff=0)
    menu.add_cascade(label="Datos", menu=menudatos)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar)
    menudatos.add_command(label="Salir", command=raiz.quit)

    # Buscar y Modificar
    menubuscar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Buscar y Modificar", menu=menubuscar)
    menubuscar.add_command(label="Eventos por población", command=eventos_por_poblacion)
    menubuscar.add_command(label="Categoría y Descripción", command=buscar_categoria_descripcion)
    menubuscar.add_command(label="Fecha y Título", command=buscar_titulo_y_fecha_inicio)
    # menubuscar.add_command(label="Modificar las fechas", command=modificar_fechas)
    menubuscar.add_command(label="Eventos que se celebran por la noche", command=eventos_noche)

    raiz.config(menu=menu)
    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()