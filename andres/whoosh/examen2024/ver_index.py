# encoding:utf-8

import argparse
import os
from datetime import datetime

from whoosh import query
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, OrGroup, QueryParser

DATE_FMT = "%d/%m/%Y"


def parse_cli_date(value):
    try:
        return datetime.strptime(value, DATE_FMT)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Formato de fecha incorrecto ('{value}'). Usa DD/MM/AAAA"
        ) from exc


def discover_index_dir(user_path):
    candidates = [user_path] if user_path else ["Index", "index", "INDEX"]
    for candidate in candidates:
        if candidate and os.path.isdir(candidate):
            return candidate
    raise FileNotFoundError(
        "No se encontro ningun directorio de indice. Usa --index para especificarlo."
    )


def escape_phrase(value):
    return '"' + value.replace('"', '\\"') + '"'


def build_query(ix, args):
    clauses = []

    if args.buscar:
        parser = MultifieldParser(["titulo", "descripcion"], ix.schema, group=OrGroup)
        clauses.append(parser.parse(args.buscar))

    if args.poblacion:
        qp = QueryParser("poblacion", ix.schema)
        clauses.append(qp.parse(escape_phrase(args.poblacion)))

    if args.categoria:
        qp = QueryParser("categorias", ix.schema)
        clauses.append(qp.parse(escape_phrase(args.categoria)))

    if clauses:
        return query.And(clauses) if len(clauses) > 1 else clauses[0]
    return query.Every()


def matches_date_filters(hit, args):
    inicio = hit.get("fecha_inicio")
    fin = hit.get("fecha_fin")

    if args.fecha_desde:
        # Requiere solapamiento con el rango [fecha_desde, ...]
        if fin and fin < args.fecha_desde:
            return False
        if not fin and inicio and inicio < args.fecha_desde:
            return False

    if args.fecha_hasta:
        if inicio and inicio > args.fecha_hasta:
            return False
        if not inicio and fin and fin > args.fecha_hasta:
            return False

    return True


def format_date_range(inicio, fin):
    if inicio and fin:
        if inicio.date() == fin.date():
            return inicio.strftime(DATE_FMT)
        return f"{inicio.strftime(DATE_FMT)} - {fin.strftime(DATE_FMT)}"
    if inicio:
        return inicio.strftime(DATE_FMT)
    if fin:
        return fin.strftime(DATE_FMT)
    return "-"


def print_event(hit, idx):
    titulo = hit.get("titulo", "(Sin titulo)")
    lugar = hit.get("lugar", "-")
    poblacion = hit.get("poblacion", "-")
    categoria = hit.get("categorias", "-")
    horas = hit.get("horas", "-")
    descripcion = (hit.get("descripcion") or "").strip()

    print(f"[{idx:02d}] {titulo}")
    print(f"    Lugar: {lugar} ({poblacion})")
    print(f"    Categoria: {categoria}")
    print(f"    Fechas: {format_date_range(hit.get('fecha_inicio'), hit.get('fecha_fin'))}")
    print(f"    Hora: {horas}")
    if descripcion:
        resumen = descripcion if len(descripcion) <= 220 else descripcion[:217].rstrip() + "..."
        print(f"    Descripcion: {resumen}")
    print()


def build_parser():
    parser = argparse.ArgumentParser(
        description="Visualizador de eventos almacenados en el indice Whoosh",
    )
    parser.add_argument(
        "--index",
        help="Ruta al directorio del indice (por defecto busca Index/index en el cwd)",
    )
    parser.add_argument("--poblacion", help="Filtra por nombre de poblacion (frase exacta)")
    parser.add_argument("--categoria", help="Filtra por categoria exacta")
    parser.add_argument(
        "--buscar",
        help="Texto libre a buscar en titulo y descripcion (sintaxis Whoosh)",
    )
    parser.add_argument(
        "--fecha-desde",
        dest="fecha_desde",
        type=parse_cli_date,
        help="Filtro de fecha de inicio (DD/MM/AAAA)",
    )
    parser.add_argument(
        "--fecha-hasta",
        dest="fecha_hasta",
        type=parse_cli_date,
        help="Filtro de fecha de fin (DD/MM/AAAA)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Numero maximo de resultados (0 = sin limite, por defecto 50)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        index_dir = discover_index_dir(args.index)
        ix = open_dir(index_dir)
    except (OSError, FileNotFoundError) as exc:
        parser.error(str(exc))

    q = build_query(ix, args)

    with ix.searcher() as searcher:
        limit = None if args.limit <= 0 else args.limit
        results = searcher.search(q, limit=limit)
        count = 0
        for hit in results:
            if not matches_date_filters(hit, args):
                continue
            count += 1
            print_event(hit, count)

    if count == 0:
        print("No se encontraron eventos para los filtros indicados.")


if __name__ == "__main__":
    main()
