# encoding:latin-1

import os
from datetime import datetime
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from tkinter import *
from tkinter import messagebox

agenda = {}
# usa rutas portables (slash) para evitar invalid escape sequence
dirdocs = os.path.join("Docs", "Correos")
dirindex = "Index"
dirage = os.path.join("Docs", "Agenda")


# Crea un indice desde los documentos contenidos en dirdocs
# El indice lo crea en el directorio dirindex
def crea_index():
    def carga():
        sch = Schema(remitente=TEXT(stored=True), destinatarios=KEYWORD(stored=True), fecha=DATETIME(stored=True), asunto=TEXT(stored=True), contenido=TEXT(stored=True,phrase=False), nombrefichero=ID(stored=True))
        ix = create_in(dirindex, schema=sch)
        writer = ix.writer()
        for docname in os.listdir(dirdocs):
            full = os.path.join(dirdocs, docname)
            if not os.path.isdir(full):
                add_doc(writer, dirdocs, docname)                  
        writer.commit()
        messagebox.showinfo("INDICE CREADO", "Se han cargado " + str(ix.reader().doc_count()) + " documentos")

    if not os.path.exists(dirdocs):
        messagebox.showerror("ERROR", "No existe el directorio de documentos " + dirdocs)
        return
    # crear dirindex si no existe
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    # ahora es seguro listar dirindex
    if os.listdir(dirindex):
        respuesta = messagebox.askyesno("Confirmar", "Indice no vacío. Desea reindexar?")
        if respuesta:
            carga()
    else:
        carga()


def asunto_o_cuerpo():
    def listar_asunto_o_cuerpo(event):
            ix=open_dir(dirindex)   
            with ix.searcher() as searcher:
                myquery = MultifieldParser(["asunto", "contenido"], ix.schema).parse(str(entry.get()))
                results = searcher.search(myquery)
                listar(results)
    v = Toplevel()
    label = Label(v, text="Introduzca consulta sobre asunto o contenido: ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar_asunto_o_cuerpo)
    entry.pack(side=LEFT)


def posteriores_a_fecha():  
    def listar_fecha(event):
            myquery='{'+ str(entry.get()) + ' TO]'
            ix=open_dir(dirindex)   
            try:
                with ix.searcher() as searcher:
                    query = QueryParser("fecha", ix.schema).parse(myquery)
                    results = searcher.search(query)
                    listar(results)
            except:
                messagebox.showerror("ERROR", "Formato de fecha incorrecto")

    v = Toplevel()
    label = Label(v, text="Introduzca la fecha (AAAAMMDD): ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar_fecha)
    entry.pack(side=LEFT)


def spam():
    def listar_spam(event):
        ix = open_dir(dirindex)
        with ix.searcher() as searcher:
            query = QueryParser("asunto", ix.schema, group=qparser.OrGroup).parse(str(entry.get()))
            results = searcher.search(query)

            v1 = Toplevel()
            sc = Scrollbar(v1)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v1, width=100, yscrollcommand=sc.set)
            for row in results:
                s = 'FICHERO: ' + row['nombrefichero']
                lb.insert(END, s)
                s = 'REMITENTE: ' + agenda[row['remitente']]
                lb.insert(END, s)
                lb.insert(END, "-------------------------------")       
            lb.pack(side=LEFT, fill=BOTH)
            sc.config(command=lb.yview)        
    v = Toplevel()
    label = Label(v, text="Introduzca palabras spam: ")
    label.pack(side=LEFT)
    entry = Entry(v)
    entry.bind("<Return>", listar_spam)
    entry.pack(side=LEFT)           


def add_doc(writer, path, docname):
    try:
        filepath = os.path.join(path, docname)
        fileobj = open(filepath, "r")
        rte = fileobj.readline().strip()
        dtos = fileobj.readline().strip()
        f = fileobj.readline().strip()
        dat = datetime.strptime(f, '%Y%m%d')
        ast = fileobj.readline().strip()
        ctdo = fileobj.read()
        fileobj.close()

        writer.add_document(remitente=rte, destinatarios=dtos, fecha=dat, asunto=ast, contenido=ctdo, nombrefichero=docname)

    except Exception as ex:
        messagebox.showerror("ERROR", "Error: No se ha podido añadir el documento " + filepath + "\n" + str(ex))


def crea_agenda():
    filepath = os.path.join(dirage, "agenda.txt")
    if not os.path.exists(filepath):
        messagebox.showerror("ERROR", "No existe el fichero de agenda: " + filepath)
        return
    try:
        with open(filepath, "r", encoding="latin-1") as fileobj:
            email = fileobj.readline()
            while email:
                nombre = fileobj.readline()
                if not nombre:
                    break
                agenda[email.strip()] = nombre.strip()
                email = fileobj.readline()
    except Exception as ex:
        messagebox.showerror("ERROR", "No se ha podido crear la agenda. Compruebe " + filepath + "\n" + str(ex))


def cargar():
    crea_index()
    crea_agenda()


def listar(results):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in results:
        s = 'REMITENTE: ' + row['remitente']
        lb.insert(END, s)       
        s = "DESTINATARIOS: " + row['destinatarios']
        lb.insert(END, s)
        s = "FECHA: " + row['fecha'].strftime('%d-%m-%Y')
        lb.insert(END, s)
        s = "ASUNTO: " + row['asunto']
        lb.insert(END, s)
        s = "CUERPO: " + row['contenido']
        lb.insert(END, s)
        lb.insert(END,"------------------------------------------------------------------------\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def ventana_principal():
    def listar_todo():
        ix = open_dir(dirindex)
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            listar(results) 

    raiz = Tk()

    menu = Menu(raiz)

    # DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar_todo)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    # BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Asunto o Cuerpo", command=asunto_o_cuerpo)
    menubuscar.add_command(label="Posteriores a una Fecha", command=posteriores_a_fecha)
    menubuscar.add_command(label="Spam", command=spam)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
