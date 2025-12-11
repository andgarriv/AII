from pathlib import Path
from main.models import Artista, Etiqueta, UsuarioArtista, UsuarioEtiquetaArtista

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# Robust line reader for mixed encodings (Windows datasets)
def _read_lines(filename):
    filepath = DATA_DIR / filename
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(filepath, "r", encoding=enc, newline="") as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
    with open(filepath, "r", encoding="latin-1", errors="replace", newline="") as f:
        return f.readlines()


def populate():
    populate_artistas()
    populate_etiquetas()
    a_dict = populate_usuario_artista()
    t_dict = get_tag_dict()
    populate_usuario_etiqueta_artista(a_dict, t_dict)

    return (
        Artista.objects.count(),
        Etiqueta.objects.count(),
        UsuarioArtista.objects.count(),
        UsuarioEtiquetaArtista.objects.count(),
    )


# ----------------------------------------------------------------------
#   ARTISTAS
# ----------------------------------------------------------------------
def populate_artistas():
    Artista.objects.all().delete()

    lista = []
    lines = _read_lines("artists.dat")

    for line in lines:
        rip = line.rstrip("\n").split("\t")
        if not rip or rip[0] == "id":
            continue
        if len(rip) < 2:
            continue
        # pad missing optional columns (url, imagen)
        while len(rip) < 4:
            rip.append("")

        lista.append(Artista(
            artistaId=int(rip[0]),
            nombre=rip[1],
            url=rip[2] or None,
            imagen=rip[3] or None
        ))

    Artista.objects.bulk_create(lista)


# ----------------------------------------------------------------------
#   ETIQUETAS
# ----------------------------------------------------------------------
def populate_etiquetas():
    Etiqueta.objects.all().delete()

    lista = []
    lines = _read_lines("tags.dat")

    for line in lines:
        rip = line.strip().split("\t")
        if not rip or rip[0] == "tagID":
            continue
        if len(rip) != 2:
            continue

        lista.append(Etiqueta(
            tagId=int(rip[0]),
            tagValue=rip[1]
        ))

    Etiqueta.objects.bulk_create(lista)


# ----------------------------------------------------------------------
#   USUARIO - ARTISTA
# ----------------------------------------------------------------------
def populate_usuario_artista():
    """
    Devuelve un diccionario { (usuarioId, artistaId) : objeto } para acelerar
    la carga de UsuarioEtiquetaArtista.
    """
    UsuarioArtista.objects.all().delete()

    lista = []
    dict_rel = {}

    lines = _read_lines("user_artists.dat")

    # Necesitamos un diccionario de artistas para evitar consultas repetidas
    artistas = {a.artistaId: a for a in Artista.objects.all()}

    for line in lines:
        rip = line.strip().split("\t")
        if not rip or rip[0] == "userID":
            continue
        if len(rip) != 3:
            continue

        usuarioId = rip[0]
        artistaId = int(rip[1])
        tiempo = int(rip[2])

        artista = artistas.get(artistaId)
        if not artista:
            continue

        ua = UsuarioArtista(
            usuarioId=usuarioId,
            artistaId=artista,
            tiempoEscucha=tiempo
        )

        lista.append(ua)
        dict_rel[(usuarioId, artistaId)] = ua

    UsuarioArtista.objects.bulk_create(lista)

    return dict_rel


# ----------------------------------------------------------------------
#   DICCIONARIO DE ETIQUETAS
# ----------------------------------------------------------------------
def get_tag_dict():
    """Diccionario {tagId: Etiqueta}"""
    return {t.tagId: t for t in Etiqueta.objects.all()}


# ----------------------------------------------------------------------
#   USUARIO - ETIQUETA - ARTISTA
# ----------------------------------------------------------------------
def populate_usuario_etiqueta_artista(ua_dict, tag_dict):
    UsuarioEtiquetaArtista.objects.all().delete()

    lista = []

    # tambien necesitamos diccionario de artistas
    artistas = {a.artistaId: a for a in Artista.objects.all()}

    lines = _read_lines("user_taggedartists.dat")

    for line in lines:
        rip = line.strip().split("\t")
        if not rip or rip[0] == "userID":
            continue
        if len(rip) < 3:
            continue

        usuarioId = rip[0]
        artistaId = int(rip[1])
        tagId = int(rip[2])

        artista = artistas.get(artistaId)
        tag = tag_dict.get(tagId)
        if not artista or not tag:
            continue

        lista.append(UsuarioEtiquetaArtista(
            usuarioId=usuarioId,
            artistaId=artista,
            tagId=tag
        ))

    UsuarioEtiquetaArtista.objects.bulk_create(lista)

    return lista
