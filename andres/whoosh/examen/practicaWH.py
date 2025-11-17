# encoding:utf-8

from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME
from whoosh.qparser import QueryParser
from whoosh import query, scoring


PAGINAS = 4  # número de páginas

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="¿Esta seguro que quiere recargar los datos?. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_datos()


def extraer_eventos():
    lista = []
    for p in range(1, PAGINAS + 1):
        url = "https://sevilla.cosasdecome.es/eventos/filtrar?pg=" + str(p)
        headers={'User-Agent': 'Mozilla/5.0'}
        f = urllib.request.urlopen(urllib.request.Request(url,headers=headers))
        s = BeautifulSoup(f,"lxml")
        eventos = s.find_all("div", class_="post-details")

        for e in eventos:
            titulo = e.find("h2", class_="nombre")
            if titulo:
                titulo = titulo.get_text().strip()
            poblacion = e.find("div", class_="poblacion")
            if poblacion:
                poblacion = poblacion.find("a").get_text().strip()
            enlace = e.find("div", class_="showmore")
            if enlace:
                enlace = enlace.find("a")["href"].strip()
            fecha = e.find("div", class_="fechas")
            if fecha:
                fecha = fecha.get_text().strip()
            m = re.findall(r'\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}', fecha)
            if len(m) >= 2:
                fecha_inicio = datetime.strptime(m[0], '%d/%m/%Y')
                fecha_fin    = datetime.strptime(m[1], '%d/%m/%Y')
            elif len(m) == 1:
                fecha_inicio = datetime.strptime(m[0], '%d/%m/%Y')
                fecha_fin = fecha_inicio
            else:
                fecha_inicio = fecha_fin = None

            categorias = e.find("div", class_="categoria")
            if categorias:
                categorias = categorias.find("a").get_text().strip()

            lista.append((titulo, poblacion, enlace, fecha_inicio, fecha_fin, categorias))
    return lista


def almacenar_datos():
    sch = Schema(titulo=TEXT(stored=True), poblacion=KEYWORD(stored=True, commas=True), enlace=TEXT, fecha_inicio=DATETIME(stored=True), fecha_fin=DATETIME(stored=True), categorias=KEYWORD(stored=True, commas=True))

    #eliminamos el directorio del índice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    ix = create_in("Index", schema=sch)
    writer = ix.writer()

    i=0
    eventos= extraer_eventos()
    for r in eventos:
        writer.add_document(titulo=r[0], poblacion=r[1], enlace=r[2], fecha_inicio=r[3], fecha_fin=r[4], categorias=r[5])
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i) + " eventos")


def imprimir_lista_eventos(cursor):
    v = Toplevel()
    v.title("Lista de eventos")

    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)

    lb = Listbox(v, width=130, height=30, yscrollcommand=sc.set, font=("Consolas", 10))

    for row in cursor:
        titulo = row.get('titulo', '') or "—"
        poblacion = row.get('poblacion', '') or "—"
        f_ini = row.get('fecha_inicio', '')
        f_fin = row.get('fecha_fin', '')
        categorias = row.get('categorias', '') or "—"

        def _fmt_fecha(f):
            if not f:
                return "—"
            if isinstance(f, datetime):
                return f.strftime("%d/%m/%Y")
            return str(f)

        f_ini_txt = _fmt_fecha(f_ini)
        f_fin_txt = _fmt_fecha(f_fin)

        lb.insert(END, f" {titulo}")
        lb.insert(END, f"    Población: {poblacion}")
        lb.insert(END, f"    Fecha inicio: {f_ini_txt}")
        lb.insert(END, f"    Fecha fin:    {f_fin_txt}")
        lb.insert(END, f"    Categorías: {categorias}")
        lb.insert(END, "-" * 100)

    lb.pack(side=LEFT, fill=BOTH, expand=True)
    sc.config(command=lb.yview)



def listar():
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        results = searcher.search(query.Every(), limit=None)
        imprimir_lista_eventos(results)


def buscar_por_titulo():
    v = Toplevel()
    v.title("Buscar por título")

    Label(v, text="Palabras en el título:").pack(side=LEFT, padx=4)
    e = Entry(v, width=50)
    e.pack(side=LEFT, padx=4)

    def ejecutar(event=None):
        texto = e.get().strip()
        if not texto:
            messagebox.showwarning("Aviso", "Introduzca una o varias palabras.")
            return
        ix = open_dir("Index")
        with ix.searcher() as s:
            terms = [t for t in re.split(r"\s+", texto) if t]
            consulta = " OR ".join(terms) if len(terms) > 1 else texto

            qp = QueryParser("titulo", ix.schema)
            q = qp.parse(consulta)
            results = s.search(q, limit=15)
            imprimir_lista_eventos(results)

    e.bind("<Return>", ejecutar)
    Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=6)


def eventos_por_poblacion():
    ix = open_dir("Index")
    with ix.searcher() as s:
        poblaciones = sorted([
            (p.decode('utf-8','ignore') if isinstance(p, bytes) else str(p))
            for p in s.lexicon("poblacion")
        ])

    v = Toplevel()
    v.title("Eventos por población")

    Label(v, text="Población:").pack(side=LEFT, padx=4)
    sp = Spinbox(v, values=poblaciones, state="readonly", width=40)
    sp.pack(side=LEFT, padx=4)

    def ejecutar():
        pob = sp.get().strip()
        if not pob:
            messagebox.showwarning("Aviso", "Seleccione una población.")
            return
        with ix.searcher() as s:
            q = query.Term("poblacion", pob)
            results = s.search(q, limit=None)
            imprimir_lista_eventos(results)

    Button(v, text="Mostrar", command=ejecutar).pack(side=LEFT, padx=6)


def categoria_y_titulo():
    ix = open_dir("Index")
    with ix.searcher() as s:
        categorias = sorted([
            (c.decode("utf-8", "ignore") if isinstance(c, bytes) else str(c))
            for c in s.lexicon("categorias")
        ])

    v = Toplevel()
    v.title("Categoría y Título")

    Label(v, text="Categoría:").pack(side=LEFT, padx=4)
    sp = Spinbox(v, values=categorias, state="readonly", width=40)
    sp.pack(side=LEFT, padx=4)

    Label(v, text="Frase a excluir del título:").pack(side=LEFT, padx=4)
    en = Entry(v, width=45)
    en.pack(side=LEFT, padx=4)

    def ejecutar():
        cat = sp.get().strip()
        frase_raw = en.get().strip()

        if not cat:
            messagebox.showwarning("Aviso", "Seleccione una categoría.")
            return

        with ix.searcher() as s:
            def intentar_consulta(q_cat, frase_raw):
                if not frase_raw:
                    return list(s.search(q_cat, limit=3))

                parser = QueryParser("titulo", ix.schema)
                try:
                    q_titulo = parser.parse(f'"{frase_raw}"')
                    q_no_frase = query.Not(q_titulo)
                    q_final = query.And([q_cat, q_no_frase])
                    return list(s.search(q_final, limit=3))
                except Exception:
                    return []

            q_cat = query.Term("categorias", cat)
            hits = intentar_consulta(q_cat, frase_raw)

            if not hits:
                q_cat_l = query.Term("categorias", cat.lower())
                hits = intentar_consulta(q_cat_l, frase_raw)

            if not hits:
                try:
                    raw = s.search(q_cat, limit=None)
                except Exception:
                    try:
                        raw = s.search(q_cat_l, limit=None)
                    except Exception:
                        raw = []

                if frase_raw:
                    frase_lower = frase_raw.lower()
                    filtrados = [h for h in raw if frase_lower not in (h.get("titulo", "") or "").lower()]
                else:
                    filtrados = list(raw)

                hits = filtrados[:3]

            if not hits:
                messagebox.showinfo("Sin resultados", "No hay eventos que cumplan los criterios.")
                return

            r = Toplevel(v)
            r.title("Resultados")
            sc = Scrollbar(r)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(r, width=120, yscrollcommand=sc.set)
            for h in hits:
                lb.insert(END, h.get("titulo", "—"))
                lb.insert(END, f"    Población: {h.get('poblacion','—')}")
                lb.insert(END, f"    Categorías: {h.get('categorias','—')}")
                lb.insert(END, "-" * 100)
            lb.pack(side=LEFT, fill=BOTH)
            sc.config(command=lb.yview)

    Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=6)


def fecha_y_titulo():
    v = Toplevel()
    v.title("Fecha y Título")

    Label(v, text="Fecha (AAAAMMDD):").pack(side=LEFT, padx=4)
    e_fecha = Entry(v, width=10)
    e_fecha.pack(side=LEFT, padx=4)

    Label(v, text="Palabras del título (todas):").pack(side=LEFT, padx=4)
    e_titulo = Entry(v, width=40)
    e_titulo.pack(side=LEFT, padx=4)

    def ejecutar():
        fecha_txt = e_fecha.get().strip()
        titulo_txt = e_titulo.get().strip()

        if not re.fullmatch(r"\d{8}", fecha_txt):
            messagebox.showerror("ERROR", "Formato de fecha incorrecto. Use AAAAMMDD (p. ej., 20251205).")
            return
        try:
            target_date = datetime.strptime(fecha_txt, "%Y%m%d").date()
        except Exception:
            messagebox.showerror("ERROR", "Fecha no válida.")
            return

        try:
            ix = open_dir("Index")
        except Exception:
            messagebox.showerror("Sin índice", "No se encuentra el índice. Use Datos → Cargar para crear el índice.")
            return

        with ix.searcher() as s:
            terms = [t for t in re.split(r"\s+", titulo_txt) if t]
            if terms:
                consulta = " AND ".join(terms)
                qp = QueryParser("titulo", ix.schema)
                q_titulo = qp.parse(consulta)
                candidatos = list(s.search(q_titulo, limit=None))
            else:
                candidatos = list(s.search(query.Every(), limit=None))

            def incluye_fecha(hit):
                fi = hit.get("fecha_inicio")
                ff = hit.get("fecha_fin") or fi

                if fi is None:
                    return False

                def to_date(x):
                    if x is None:
                        return None
                    if isinstance(x, datetime):
                        return x.date()
                    if isinstance(x, str):
                        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                            try:
                                return datetime.strptime(x, fmt).date()
                            except Exception:
                                pass
                    return None

                fi_d = to_date(fi)
                ff_d = to_date(ff) or fi_d

                if fi_d is None:
                    return False
                return fi_d <= target_date <= ff_d

            resultados = [h for h in candidatos if incluye_fecha(h)]

        if not resultados:
            messagebox.showinfo("Sin resultados", "No hay eventos que cumplan los criterios.")
            return

        imprimir_lista_eventos(resultados)

    Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=6)
    e_fecha.bind("<Return>", lambda _: ejecutar())
    e_titulo.bind("<Return>", lambda _: ejecutar())


def modificar_fechas():
    v = Toplevel()
    v.title("Modificar fechas")

    frm = Frame(v)
    frm.pack(padx=10, pady=10)

    Label(frm, text="Fecha a buscar (DD-MM-AAAA):").grid(row=0, column=0, sticky=W, pady=3)
    e_fecha_buscar = Entry(frm, width=12)
    e_fecha_buscar.grid(row=0, column=1, sticky=W, pady=3)
    e_fecha_buscar.focus_set()

    Label(frm, text="Nueva fecha (DD-MM-AAAA):").grid(row=1, column=0, sticky=W, pady=3)
    e_fecha_nueva = Entry(frm, width=12)
    e_fecha_nueva.grid(row=1, column=1, sticky=W, pady=3)

    def ejecutar():
        fecha_txt = e_fecha_buscar.get().strip()
        nueva_txt = e_fecha_nueva.get().strip()

        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", fecha_txt):
            messagebox.showerror("ERROR", "Formato de la fecha a buscar incorrecto. Use DD-MM-AAAA (p. ej., 05-12-2025).")
            return
        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", nueva_txt):
            messagebox.showerror("ERROR", "Formato de la nueva fecha incorrecto. Use DD-MM-AAAA (p. ej., 05-12-2025).")
            return

        try:
            target_date = datetime.strptime(fecha_txt, "%d-%m-%Y").date()
            nueva_date = datetime.strptime(nueva_txt, "%d-%m-%Y")
        except Exception:
            messagebox.showerror("ERROR", "Alguna de las fechas no es válida.")
            return

        # Abrir índice
        try:
            ix = open_dir("Index")
        except Exception:
            messagebox.showerror("Sin índice", "No se encuentra el índice. Use Datos → Cargar para crear el índice.")
            return

        candid_docnums = []
        with ix.searcher() as s:
            resultados = s.search(query.Every(), limit=None)

            for h in resultados:
                fi = h.get("fecha_inicio")
                ff = h.get("fecha_fin") or fi

                def to_date(x):
                    if x is None:
                        return None
                    if isinstance(x, datetime):
                        return x.date()
                    if isinstance(x, str):
                        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                            try:
                                return datetime.strptime(x, fmt).date()
                            except Exception:
                                pass
                    return None

                fi_d = to_date(fi)
                ff_d = to_date(ff) or fi_d

                if fi_d is not None and fi_d <= target_date <= ff_d:
                    candid_docnums.append(h.docnum)

        total = len(candid_docnums)
        if total == 0:
            messagebox.showinfo("Sin resultados", "No hay eventos que se celebren en esa fecha.")
            return

        confirmar = messagebox.askyesno(
            title="Confirmar modificación",
            message=f"Se han encontrado {total} evento(s) en la fecha {fecha_txt}.\n"
                    f"¿Desea actualizar esas fechas a {nueva_txt}?",
            icon="question"
        )
        if not confirmar:
            return

        writer = ix.writer()
        try:
            with ix.searcher() as s:
                for docnum in candid_docnums:
                    stored = s.stored_fields(docnum)
                    writer.delete_document(docnum)

                    fecha_fin_val = stored.get("fecha_fin")
                    if fecha_fin_val == stored.get("fecha_inicio"):
                        fecha_fin_val = nueva_date

                    writer.add_document(
                        titulo=stored.get("titulo", ""),
                        poblacion=stored.get("poblacion", ""),
                        enlace=stored.get("enlace", ""),
                        fecha_inicio=nueva_date,
                        fecha_fin=fecha_fin_val,
                        categorias=stored.get("categorias", "")
                    )
            writer.commit()
            messagebox.showinfo("Éxito", f"Se han modificado {total} evento(s).")
        except Exception as e:
            writer.cancel()
            messagebox.showerror("Error", f"No se pudieron modificar las fechas.\n{e}")

    btn = Button(frm, text="Modificar", command=ejecutar)
    btn.grid(row=2, column=1, sticky=E, pady=(8, 0))

    e_fecha_buscar.bind("<Return>", lambda _: ejecutar())
    e_fecha_nueva.bind("<Return>", lambda _: ejecutar())


def titulo_por_subcadena():
    v = Toplevel()
    v.title("Título por Subcadena")

    Label(v, text="Prefijo (sin espacios):").pack(side=LEFT, padx=4)
    e = Entry(v, width=30)
    e.pack(side=LEFT, padx=4)

    def ejecutar(event=None):
        pref = (e.get() or "").strip()
        if not pref or not re.match(r"^\S+$", pref):
            messagebox.showerror("ERROR", "Introduzca una cadena sin espacios (ej.: conci).")
            return

        ix = open_dir("Index")
        with ix.searcher(weighting=scoring.TF_IDF()) as s:
            q = query.Prefix("titulo", pref.lower())
            hits = s.search(q, limit=5)

            if not hits:
                messagebox.showinfo("Sin resultados", "No hay títulos que empiecen por ese prefijo.")
                return

            r = Toplevel(v)
            r.title("Títulos encontrados")
            sc = Scrollbar(r)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(r, width=100, yscrollcommand=sc.set)
            for h in hits:
                lb.insert(END, h.get("titulo", "—"))
                lb.insert(END, "-" * 100)
            lb.pack(side=LEFT, fill=BOTH)
            sc.config(command=lb.yview)

    e.bind("<Return>", ejecutar)
    Button(v, text="Buscar", command=ejecutar).pack(side=LEFT, padx=6)


def ventana_principal():
    raiz = Tk()
    raiz.geometry("1200x600")
    raiz.title("Cosas de Comé")

    menu = Menu(raiz)

    # Datos
    menudatos = Menu(menu, tearoff=0)
    menu.add_cascade(label="Datos", menu=menudatos)
    menudatos.add_command(label="Cargar", command=cargar)
    menudatos.add_command(label="Listar", command=listar)
    menudatos.add_command(label="Salir", command=raiz.quit)

    # Buscar y Modificar
    menubuscar = Menu(menu, tearoff=0)
    menu.add_cascade(label="Buscar", menu=menubuscar)
    menubuscar.add_command(label="Titulo", command=buscar_por_titulo)
    menubuscar.add_command(label="Eventos por población", command=eventos_por_poblacion)
    menubuscar.add_command(label="Categoría y Titulo", command=categoria_y_titulo)
    menubuscar.add_command(label="Fecha y Título", command=fecha_y_titulo)
    menubuscar.add_command(label="Modificar fechas", command=modificar_fechas)
    menubuscar.add_command(label="Título por Subcadena", command=titulo_por_subcadena)

    raiz.config(menu=menu)
    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()
