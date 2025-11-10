#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID
from whoosh.qparser import QueryParser
from datetime import datetime
import locale

PAGINAS = 2  #nÃºmero de pÃ¡ginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. \nEsta operaciÃ³n puede ser lenta")
    if respuesta:
        almacenar_datos()
        
def extraer_noticias():
    locale.setlocale(locale.LC_TIME, "es_ES") # activa formato en espaÃ±ol
    
    lista=[]
    
    for p in range(1,PAGINAS+1):
        req = urllib.request.Request("https://muzikalia.com/category/noticia/page/"+str(p)+"/", headers={'User-Agent': 'Mozilla/5.0'})
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, 'lxml')
        l = s.find_all('article', class_='category-noticia')

        for i in l:
            titulo = i.find('h2', class_='cm-entry-title').a.string
            enlace = i.find('h2', class_='cm-entry-title').a['href']
            d = i.find('time').string
            fecha = datetime.strptime(d.strip(), "%d %B, %Y")
            descripcion = i.find('div', class_='cm-entry-summary').p.string
            autor = i.find('span',class_='cm-author').a.string.strip()
                                          
            lista.append((fecha, titulo, enlace, descripcion, autor))
    return lista


def imprimir_lista(cursor):
    locale.setlocale(locale.LC_TIME, "es_ES") # activa formato en espaÃ±ol
    
    v = Toplevel()
    v.title("NOTICIAS DE MUSIKALIA")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row['titulo'])
        lb.insert(END,"    Autor: "+ str(row['autor']))
        lb.insert(END,"    Fecha: "+ datetime.strftime(row['fecha'], "%d de %B de %Y"))
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

 
def almacenar_datos():
    #define el esquema de la informaciÃ³n
    schem = Schema(fecha=DATETIME(stored=True), titulo=TEXT(stored=True), enlace=ID, descripcion=TEXT, autor=ID(stored=True))
    
    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el Ã­ndice
    ix = create_in("Index", schema=schem)
    #creamos un writer para poder aÃ±adir documentos al indice
    writer = ix.writer()
    i=0
    lista=extraer_noticias()
    for j in lista:
        #aÃ±ade cada juego de la lista al Ã­ndice
        writer.add_document(fecha=j[0], titulo=str(j[1]), enlace=str(j[2]), descripcion=str(j[3]), autor=str(j[4]))    
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " noticias")          


def buscar_autor():
    def mostrar_lista(event):    
        with ix.searcher() as searcher:
            entrada = '"'+str(en.get().strip())+'"'
            query = QueryParser("autor", ix.schema).parse(entrada)
            results = searcher.search(query,limit=None)
            imprimir_lista(results)
    
    
    v = Toplevel()
    v.title("BÃºsqueda por Autor")
    l = Label(v, text="Seleccione autor a buscar:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    with ix.searcher() as searcher:
        #lista de todas los autores
        lista_autores = [i.decode('utf-8') for i in searcher.lexicon('autor')]
    
    en = Spinbox(v, values=lista_autores, state="readonly")
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)


def buscar_fecha_y_titulo():
    def mostrar_lista():
        ix=open_dir("Index")   
        with ix.searcher() as searcher:
            s = re.compile('\d{8}').match(str(en.get()))
            if s:
                query = QueryParser("titulo", ix.schema).parse('fecha:['+ str(en.get()) +' TO] '+ str(en1.get()))
                results = searcher.search(query,limit=None)
                imprimir_lista(results)
            else:
                messagebox.showerror("ERROR", "formato de fecha incorrecto AAAAMMDD")
    
    v = Toplevel()
    v.title("BÃºsqueda por Fecha y TÃ­tulo")
    l = Label(v, text="Escriba una fecha (AAAAMMDD):")
    l.pack(side=LEFT)   
    en = Entry(v)
    en.pack(side=LEFT)
    
    l1 = Label(v, text="Escriba palabras del tÃ­tulo:")
    l1.pack(side=LEFT)
    en1 = Entry(v, width=75)
    en1.pack(side=LEFT)
    
    b =Button(v, text="Buscar", command=mostrar_lista)
    b.pack(side=LEFT)
    
    
def eliminar_por_descripcion():
    def modificar(event):
        ix=open_dir("Index") 
        with ix.searcher() as searcher:
            query = QueryParser("descripcion", ix.schema).parse(str(en.get()))
            results = searcher.search(query, limit=None)
            if len(results) > 0: # si hay algÃºn documento a borrar 
                v = Toplevel()
                v.title("Listado de Noticias a Borrar")
                v.geometry('800x150')
                sc = Scrollbar(v)
                sc.pack(side=RIGHT, fill=Y)
                lb = Listbox(v, yscrollcommand=sc.set)
                lb.pack(side=BOTTOM, fill = BOTH)
                sc.config(command = lb.yview)
                for r in results:
                    lb.insert(END,r['titulo'])
                    lb.insert(END,'')
                # pedimos confirmaciÃ³n
                respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere eliminar estas noticias?")
                if respuesta:
                    writer = ix.writer()
                    writer.delete_by_query(query)
                    writer.commit()
            else:
                messagebox.showinfo("AVISO", "No hay ninguna noticia con esas palabras en la descripciÃ³n")

    v = Toplevel()
    v.title("Eliminar Noticias por DescripciÃ³n")
    l = Label(v, text="Introduzca palabras en la descripciÃ³n:")
    l.pack(side=LEFT)
    en = Entry(v, width=75)
    en.bind("<Return>", modificar)
    en.pack(side=LEFT)

    

def ventana_principal():       
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=almacenar_datos)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Autor", command=buscar_autor)
    buscarmenu.add_command(label="Fecha y TÃ­tulo", command=buscar_fecha_y_titulo)
    buscarmenu.add_command(label="Eliminar por DescripciÃ³n", command=eliminar_por_descripcion)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    ventana_principal()