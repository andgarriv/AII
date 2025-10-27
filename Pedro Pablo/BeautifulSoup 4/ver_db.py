import sqlite3, os
db = 'temporadas.db'
print('Buscando:', db)
print('Existe:', os.path.exists(db))
if not os.path.exists(db):
    raise SystemExit('No se encuentra ' + db + ' en esta carpeta. Ejecuta tu script primero.')

conn = sqlite3.connect(db)
cur = conn.cursor()
print('Tablas:', [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")])
try:
    total = cur.execute("SELECT COUNT(*) FROM TEMPORADAS").fetchone()[0]
    print('Registros TEMPORADAS:', total)
    print('Primeras 20 filas:')
    for row in cur.execute("SELECT JORNADA, LOCAL, VISITANTE, MARCADOR, GOLES_LOCAL, GOLES_VISITANTE, LINK FROM TEMPORADAS LIMIT 20"):
        print(row)
except Exception as e:
    print('Error consultando TEMPORADAS:', e)
conn.close()