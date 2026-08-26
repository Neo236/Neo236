"""Arma el README.md a partir de las bandas generadas y las piezas en vivo.

Se importa desde render.py: primero se generan los SVG, despues se escribe el
README que los referencia. Asi el markdown tambien es un artefacto reproducible
y no se edita a mano.
"""
from __future__ import annotations

from urllib.parse import quote

RAW = "https://raw.githubusercontent.com/Neo236/Neo236"


def _atr(texto: str) -> str:
    """Escapa un valor de atributo HTML.

    Sin esto, un '>' dentro de alt (p. ej. "deploy > dormir") cierra la
    etiqueta <img> y el resto del tag se imprime como texto en el perfil.
    """
    return (texto.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace('"', "&quot;"))


def _banda(nombre: str, alt: str, version: str) -> str:
    d = f"{RAW}/main/assets/bandas/{nombre}-dark.svg?v={version}"
    c = f"{RAW}/main/assets/bandas/{nombre}-light.svg?v={version}"
    return ('<picture>\n'
            f'  <source media="(prefers-color-scheme: dark)" srcset="{d}">\n'
            f'  <img alt="{_atr(alt)}" src="{c}">\n'
            '</picture>')


def _par(oscuro: str, claro: str, alt: str, ancho: int | None = None) -> str:
    w = f' width="{ancho}"' if ancho else ""
    return ('<picture>\n'
            f'  <source media="(prefers-color-scheme: dark)" srcset="{_atr(oscuro)}">\n'
            f'  <img alt="{_atr(alt)}"{w} src="{_atr(claro)}">\n'
            '</picture>')


def _url_typing(cfg: dict, C: dict) -> str:
    """Arma la URL del typing para un modo, tomando los colores de los tokens."""
    p = dict(cfg["parametros"])
    p["color"] = C["texto/titulo"].lstrip("#")
    p["background"] = C["fondo/base"].lstrip("#")
    p["borderColor"] = C["borde/sutil"].lstrip("#")
    partes = []
    for k, v in p.items():
        if isinstance(v, bool):
            v = "true" if v else "false"
        partes.append(f"{k}={quote(str(v))}")
    # el separador de lineas es ';', asi que un ';' dentro de una frase la parte:
    # se codifica junto con el resto de caracteres reservados
    lineas = ";".join(quote(l, safe="") for l in cfg["lineas"])
    return cfg["base"] + "?" + "&".join(partes) + "&lines=" + lineas


ALTS = {
    "cabecera": "neo236@pastizal:~$ whoami — Lautaro «Neo» Mambrin, Chrysocyon brachyurus subsp. fullstackurus, espécimen Nº 236",
    "presentacion": "neo236@pastizal:~$ ./presentacion --loop",
    "man": ("man aguara-guazu — Subespecie fullstackurus: desarrollador fullstack endémico del Chaco. "
            "Backend en Java con Spring Boot y Python con FastAPI; frontend en React y Next.js con TypeScript. "
            "Infra propia en Oracle Cloud con Docker. Game dev en C# y Unity."),
    "procesos": "ps aux | grep trabajando_en — Energi AI, Oracle Next Education, UNIX Soluciones, game dev",
    "destacado": "git show destacado — Energi AI: IA aplicada a energía, Hackathon ONE G9 – LATAM con No Country",
    "stack": ("tree ~/stack — backend: Java/Spring Boot, Python/FastAPI, Node/Express. "
              "frontend: React/Vite, Next.js/Tailwind. datos: PostgreSQL, MySQL, MongoDB, SQLite, Redis. "
              "infra: Docker, OCI. gamedev: C#, ShaderLab, HLSL."),
    "huellas": "neo236@pastizal:~$ ./huellas.sh --live",
    "cierre": "despierto desde ayer · deploy > dormir · exit 0",
    "pastizal": "",
}


def construir(texto: dict, version: str, oscuro: dict, claro: dict, rampa: dict) -> str:
    v = texto["vivas"]
    b = lambda n: _banda(n, ALTS[n], version)

    partes = [
        "<!--",
        "  Este README se genera. NO editarlo a mano:",
        "    - el texto vive en  render/contenido.yml",
        "    - los colores en    render/tokens.json  (exportados de Figma)",
        "    - la maquetacion en render/src/render.py",
        "  Regenerar:  py -3.13 render/src/render.py",
        "  Creditos de todo lo ajeno: CREDITOS.md",
        "-->",
        "",
        '<div align="center">', "",
        b("cabecera"), "",
        b("presentacion"), "",
        _par(_url_typing(texto["typing"], oscuro),
             _url_typing(texto["typing"], claro),
             "Fullstack: del server al pastizal · Cazando bugs en el pastizal · npm run madrugada"),
        "",
        b("man"), "",
        b("procesos"), "",
        "</div>", "",
        f'<a href="{texto["destacado"]["url"]}">',
        b("destacado"),
        "</a>", "",
        '<div align="center">', "",
        b("stack"), "",
        b("huellas"), "",
        _par(v["stats"].format(tema="aguara"), v["stats"].format(tema="aguara_light"),
             "Estadísticas de GitHub", 411),
        _par(v["lenguajes"].format(tema="aguara", paleta=rampa["oscuro"].replace(",", "%2C")),
             v["lenguajes"].format(tema="aguara_light", paleta=rampa["claro"].replace(",", "%2C")),
             "Lenguajes más usados", 411),
        _par(v["racha"].format(modo="dark"), v["racha"].format(modo="light"),
             "Racha de contribuciones", 411),
        f'<a href="{v["spotify_perfil"]}">',
        _par(v["spotify"].format(modo="dark"), v["spotify"].format(modo="light"),
             "Escuchando ahora en Spotify", 411),
        "</a>", "",
        _par(v["snake"].format(modo="dark"), v["snake"].format(modo="light"),
             "Snake de contribuciones recorriendo el pastizal"),
        "",
        b("cierre"), "",
        b("pastizal"), "",
        "</div>", "",
    ]
    return "\n".join(partes) + "\n"
