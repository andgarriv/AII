#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
import sqlite3
from tkinter import messagebox
from tkinter import *
import re



# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# def extraer_jornadas():
#     lista=[]
    
#     url="http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/"
#     f = urllib.request.urlopen(url)
#     s = BeautifulSoup(f,"lxml")      
    
    
#     l = s.find_all("div", class_="resultados")

    
#     for i in l:
#         jornada_id = i.get('id')
#         if jornada_id:
#             id = int(re.search(r'\d+', jornada_id).group())
#         else:
#             h = i.find(['h1','h2','h3','h4'])
#             if h and 'jornada' in h.get_text(' ', strip=True).lower():
#                 if re.search(r'\d+', h.get_text(' ', strip=True).lower()):
#                     id = int(re.search(r'\d+', h.get_text(' ', strip=True).lower()).group())
#                 else:
#                     id = l.index(i) + 1

#         partidos = i.find_all("tr")
#         for partido in partidos:
#             local = partido.find("td", class_="col-equipo-local")
#             visitante = partido.find("td", class_="col-equipo-visitante")
#             if local and visitante:
#                 nombre_local = local.find("span", class_="nombre-equipo")
#                 if nombre_local:
#                     local = nombre_local.get_text(' ', strip=True)
#                 nombre_visitante = visitante.find("span", class_="nombre-equipo")
#                 if nombre_visitante:
#                     visitante = nombre_visitante.get_text(' ', strip=True)

#             link = None
#             marcador = ''
#             resultado = partido.find("td", class_="col_resultado")
#             if resultado:
#                 reasultado_a = resultado.find("a", href=True)
#                 if reasultado_a:
#                     marcador = reasultado_a.get_text(' ', strip=True)
#                     href = reasultado_a.get('href', None)
#                     if href and href.startswith('http'):
#                         link = href
#                     else:
#                         link = 'https://as.com' + href
#                 else:
#                     marcador = resultado.get_text(' ', strip=True)
#             marcador_normalizado = (marcador or '').replace('–', '-').replace(':', '-').strip()
#             goles_local = None
#             goles_visitante = None
#             if marcador_normalizado:
#                 parts = [p.strip() for p in marcador_normalizado.split('-')]
#                 if len(parts) == 2:
#                     try:
#                         goles_local = int(parts[0])
#                         goles_visitante = int(parts[1])
#                     except:
#                         goles_local = None
#                         goles_visitante = None
        
                        
#         lista.append((
#                 id,
#                 local,
#                 visitante,
#                 marcador_normalizado,
#                 goles_local,
#                 goles_visitante,
#                 link
#         ))
        
#     return lista
def extraer_jornadas():
    lista = []

    url = "http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")

    jornadas = s.find_all("div", class_="resultados")

    for idx, bloque in enumerate(jornadas, start=1):
        jornada_num = idx
        filas = bloque.find_all("tr")
        for fila in filas:
            td_local = fila.find("td", class_="col-equipo-local")
            td_visit = fila.find("td", class_="col-equipo-visitante")
            if not td_local or not td_visit:
                continue

            span_local = td_local.find("span", class_="nombre-equipo")
            if span_local:
                local = span_local.get_text(' ', strip=True)
            else:
                a_local = td_local.find("a")
                local = a_local.get_text(' ', strip=True) if a_local else td_local.get_text(' ', strip=True)

            span_visit = td_visit.find("span", class_="nombre-equipo")
            if span_visit:
                visitante = span_visit.get_text(' ', strip=True)
            else:
                a_visit = td_visit.find("a")
                visitante = a_visit.get_text(' ', strip=True) if a_visit else td_visit.get_text(' ', strip=True)

            marcador = ''
            link = None
            resultado_td = fila.find("td", class_="col-resultado")    
            if resultado_td:
                a_res = resultado_td.find("a", href=True)
                if a_res:
                    marcador = a_res.get_text(' ', strip=True)
                    href = a_res.get('href', None)
                    if href:
                        if href.startswith('http'):
                            link = href
                        else:
                            link = 'https://as.com' + href
                else:
                    marcador = resultado_td.get_text(' ', strip=True)

            marcador_normalizado = (marcador or '').replace('–', '-').replace(':', '-').strip()
            goles_local = None
            goles_visitante = None
            if marcador_normalizado:
                parts = [p.strip() for p in marcador_normalizado.split('-')]
                if len(parts) == 2:
                    try:
                        gl = re.sub(r'\D', '', parts[0])
                        gv = re.sub(r'\D', '', parts[1])
                        goles_local = int(gl) if gl != '' else None
                        goles_visitante = int(gv) if gv != '' else None
                    except:
                        goles_local = None
                        goles_visitante = None

            local = local or ''
            visitante = visitante or ''
            marcador_val = marcador_normalizado if marcador_normalizado else None

            lista.append((
                jornada_num,
                local,
                visitante,
                marcador_val,
                goles_local,
                goles_visitante,
                link
            ))

    return lista

def almacenar_bd(db_path='temporadas.db'):
    
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS TEMPORADAS")
    conn.execute('''CREATE TABLE TEMPORADAS
       (JORNADA INTEGER,
        LOCAL TEXT,
        VISITANTE TEXT,
        MARCADOR TEXT,
        GOLES_LOCAL INTEGER,
        GOLES_VISITANTE INTEGER,
        LINK TEXT UNIQUE);''')
    conn.commit()

    resultados = extraer_jornadas()

    try:
        for r in resultados:
            try:
                conn.execute("""INSERT OR IGNORE INTO TEMPORADAS
                                (JORNADA, LOCAL, VISITANTE, MARCADOR, GOLES_LOCAL, GOLES_VISITANTE, LINK)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""", r)
            except Exception as e:
                print("Error insertando:", e, r)
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM TEMPORADAS").fetchone()[0]
        messagebox.showinfo("Base Datos", f"Base de datos creada correctamente\nHay {total} registros")
    finally:
        conn.close()

def imprimir_jornadas(cursor):
    v = Toplevel()
    v.title("Resultados por Jornada")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=120, yscrollcommand=sc.set, font=("TkFixedFont", 10))
    for jornada, local, visitante, marcador, gl, gv in cursor:
        marcador_text = marcador or (f"{gl}-{gv}" if gl is not None and gv is not None else "-")
        line = f"J{int(jornada):02d}  {local}  vs  {visitante}  |  {marcador_text}"
        lb.insert(END, line)
    lb.pack(side=LEFT, fill=BOTH, expand=True)
    sc.config(command=lb.yview)

# def imprimir_jornadas(cursor):
#     """
#     Muestra en una ventana (Listbox + scrollbar) los partidos agrupados por jornada.
#     Recibe un cursor/iterable con filas: (JORNADA, LOCAL, VISITANTE, MARCADOR, GOLES_LOCAL, GOLES_VISITANTE, [LINK])
#     Maneja tanto filas con 6 como con 7 campos (link opcional).
#     """
#     v = Toplevel()
#     v.title("Resultados por Jornada")
#     v.geometry("650x500")

#     sc = Scrollbar(v)
#     sc.pack(side=RIGHT, fill=Y)

#     lb = Listbox(v, width=100, yscrollcommand=sc.set, font=("Consolas", 10))
#     lb.pack(side=LEFT, fill=BOTH, expand=True)
#     sc.config(command=lb.yview)

#     current_j = None
#     for row in cursor:
#         # row puede tener 6 o 7 elementos; extraemos seguro por índices
#         jornada = row[0]
#         local = row[1] if len(row) > 1 else ""
#         visitante = row[2] if len(row) > 2 else ""
#         marcador = row[3] if len(row) > 3 else None
#         gl = row[4] if len(row) > 4 else None
#         gv = row[5] if len(row) > 5 else None
#         # link se ignora aquí (no se une funciones), pero lo recogemos por si necesitas usarlo luego
#         # link = row[6] if len(row) > 6 else None

#         # encabezado de jornada
#         if jornada != current_j:
#             current_j = jornada
#             lb.insert(END, f"JORNADA {int(jornada)}")
#             lb.insert(END, "-" * 60)

#         # preparar texto de marcador
#         if marcador:
#             marcador_text = marcador
#         elif gl is not None and gv is not None:
#             marcador_text = f"{gl}-{gv}"
#         else:
#             marcador_text = "-"

#         # formatear línea (local | marcador | visitante) con anchuras razonables
#         local_fmt = (local[:25]).ljust(25)
#         visitante_fmt = visitante
#         marcador_fmt = marcador_text.center(7)
#         line = f"{local_fmt}  {marcador_fmt}  {visitante_fmt}"

#         lb.insert(END, line)

#     # si no hay nada insertado, mostrar mensaje breve en la listbox
#     if lb.size() == 0:
#         lb.insert(END, "No hay partidos en la base de datos (TEMPORADAS).")

def listar_jornadas():
    conn = sqlite3.connect('temporadas.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT * FROM TEMPORADAS")
    imprimir_jornadas(cursor)
    conn.close()

def ventana_principal():       
    root = Tk()
    root.geometry("150x100")

    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=almacenar_bd)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Jornadas", command=listar_jornadas)
    buscarmenu.add_command(label="Mejores juegos")
    
    menubar.add_cascade(label="Listar", menu=buscarmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Juegos por temÃ¡tica")
    buscarmenu.add_command(label="Juegos por complejidad")
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()


if __name__ == "__main__":
    ventana_principal()