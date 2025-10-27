#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID
from whoosh.qparser import QueryParser

PAGINAS = 1  #nÃºmero de pÃ¡ginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        crea_index()


def extraer_juegos():
    lista=[]
    
    for p in range(1,PAGINAS+1):
        url="https://zacatrus.es/juegos-de-mesa.html?p="+str(p)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f,"lxml")      
        
        l = s.ol.find_all("div", class_= "product-item-details")

        for i in l:
            titulo = i.a.string.strip()
            # votos = i.find("div",class_="rating-result")
            # if votos:
            #     votos = int(re.compile(r'\d+').search(votos['title']).group())
            # else:
            #     votos = -1
            precio = re.compile(r'\d+,\d+').search(i.find("span", class_="price").string.strip()).group()
            precio = float(precio.replace(',','.'))
            
            f1 = urllib.request.urlopen(i.a['href'])
            j = BeautifulSoup(f1,"lxml")
          
            t = j.find("div", class_="data table additional-attributes")       
            if t :
                tematica = t.find("div",attrs={"data-th":"Temática"})
                if tematica:
                    tematica = tematica.string.strip()
                else:
                    tematica = "Desconocida"
                complejidad = t.find("div",attrs={"data-th":"Complejidad"})
                if complejidad:
                    complejidad = complejidad.string.strip()
                else:
                    complejidad = "Desconocida"
                jugadores = t.find("div",attrs={"data-th":"Núm. jugadores"})
                if jugadores:
                    jugadores = jugadores.string.strip()
                else:
                    jugadores = "Desconocido"
            else: #no tienen caracterÃ­sticas adicionales
                tematica = "Desconocida"
                complejidad = "Desconocida"
                jugadores = "Desconocido"
            t = j.find("div", class_="product attribute description")
            detalles = ""
            if t:
                detalles = t.get_text(separator="\n", strip=True)
            print(precio)
                    
            lista.append((titulo,precio,tematica,complejidad,jugadores,detalles))
        
    return lista

def crea_index():
    sch = Schema(titulo=TEXT(stored=True, phrase=False), precio=NUMERIC(stored=True, numtype=float), 
                 tematica=KEYWORD(stored=True, commas=True, lowercase=True), complejidad=ID(stored=True), jugadores=KEYWORD(stored=True, commas=True), detalles=TEXT)

    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    ix = create_in("Index", schema=sch)
    writer = ix.writer()

    i=0
    juegos= extraer_juegos()
    for j in juegos:
        writer.add_document(titulo=str(j[0]), precio=float(str(j[1])), tematica=str(j[2]), complejidad=str(j[3]), jugadores=str(j[4]), detalles=str(j[5]))    
        i+=1
    writer.commit()              
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " juegos")  

def imprimir_lista(cursor):
    v = Toplevel()
    v.title("JUEGOS DE MESA DE ZACATRUS")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row['titulo'])
        lb.insert(END,"    Precio: "+ str(row['precio']) + " €")
        lb.insert(END,"    Temáticas: "+ row['tematica'])
        lb.insert(END,"    Complejidad: "+ row['complejidad'])
        lb.insert(END,"    Jugadores: "+ row['jugadores'])
        lb.insert(END,"\n\n")   
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

def buscar_detalles():
    def mostrar_lista(event):
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            query = QueryParser("detalles", ix.schema).parse('"'+str(en.get())+'"')
            results = searcher.search(query,limit=10) #sÃ³lo devuelve los 10 primeros
            imprimir_lista(results)
    
    v = Toplevel()
    v.title("Búsqueda por Detalles")
    l = Label(v, text="Introduzca la frase a buscar:")
    l.pack(side=LEFT)
    en = Entry(v, width=75)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)  

def buscar_tematicas():
    def mostrar_lista(event):
        with ix.searcher() as searcher:
            query = QueryParser("tematica", ix.schema).parse('"'+str(entry.get()).lower()+'"')
            results = searcher.search(query,limit=None)
            imprimir_lista(results)
    
    v = Toplevel()
    v.title("Búsqueda por Temática")
    l = Label(v, text="Introduzca la temática a buscar:")
    l.pack(side=LEFT)

    ix=open_dir("Index")
    with ix.searcher() as searcher:
        lista_tematicas = set()
        all_terms = searcher.lexicon("tematica")
        for term in all_terms:
            lista_tematicas.add(term.decode("utf-8"))

    entry = Spinbox(v, values=sorted(lista_tematicas), state="readonly")
    entry.bind("<Return>", mostrar_lista)
    entry.pack(side=LEFT)


def ventana_principal():
    raiz = Tk()
    raiz.title("Juegos de mesa con Whoosh")
    
    menu = Menu(raiz)

    # DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    # BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Por Temática", command=buscar_tematicas)
    menubuscar.add_command(label="Por Detalles", command=buscar_detalles)
    menu.add_cascade(label="Buscar", menu=menubuscar)


    raiz.config(menu=menu)
    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()