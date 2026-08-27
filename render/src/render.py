"""Generador de bandas SVG del README de Neo236.

Cada sección del perfil se emite como un SVG independiente, en dos variantes
(oscuro/claro). Las bandas van SIN FONDO: se apoyan sobre el fondo real de
GitHub, así no hay costuras entre imágenes en ningún modo.

Editar el texto en contenido.yml y los colores en tokens.json.
La maquetación vive acá.

    py -3.13 render/src/render.py
"""
from __future__ import annotations

import base64
import io
import json
import math
import os
import re
from pathlib import Path

# fontTools estampa la hora actual en head.modified de cada subset, asi que dos
# corridas seguidas producian WOFF2 distintos y el diff tocaba las 18 bandas
# aunque no cambiara nada visual. Con esto el generador es reproducible.
os.environ.setdefault("SOURCE_DATE_EPOCH", "0")

import yaml
from fontTools import subset

import readme as armador
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ.parent / "assets" / "bandas"
TOKENS = json.loads((RAIZ / "tokens.json").read_text(encoding="utf-8"))
TEXTO = yaml.safe_load((RAIZ / "contenido.yml").read_text(encoding="utf-8"))

ANCHO = TOKENS["medidas"]["ancho"]
PROSA_MAX = TOKENS["medidas"]["prosa_max"]
AVANCE = TOKENS["tipografia"]["mono"]["avance_em"]

# ---------------------------------------------------------------- tipografía

def _instanciar(archivo: str, peso: int) -> TTFont:
    f = TTFont(RAIZ / "fuentes" / archivo)
    if "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": peso}, inplace=False)
    return f


def _subset_b64(fuente: TTFont, caracteres: str) -> str:
    opciones = subset.Options()
    opciones.flavor = "woff2"
    opciones.layout_features = []       # sin ligaduras: ancho predecible
    opciones.notdef_outline = True
    opciones.desubroutinize = True
    s = subset.Subsetter(options=opciones)
    s.populate(text=caracteres)
    s.subset(fuente)
    buf = io.BytesIO()
    fuente.flavor = "woff2"
    fuente.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


_CACHE_SUBSET: dict[tuple, str] = {}


def _fuentes_para(l: "Lienzo") -> list[tuple]:
    """Las caras que embebe UNA banda: solo las que usa y solo sus glifos.

    Antes se subseteaba una vez con todos los caracteres de todo el contenido
    y se embebia ese mismo blob en las nueve bandas: 26.8 KB repetidos ocho
    veces, el 88% del peso de las bandas, y siete de ellas cargando la serif
    sin usarla. Como cada banda es un <img> aparte no pueden compartir nada,
    asi que la unica salida es que cada una lleve lo justo.
    """
    fuentes = []
    for (fam, peso) in sorted(l.usados):
        glifos = "".join(sorted(l.usados[(fam, peso)]))
        archivo, estilo = ("Lora-Italic.ttf", "italic") if fam == "LO" else ("FiraCode-Variable.ttf", "normal")
        clave = (archivo, peso, glifos)
        if clave not in _CACHE_SUBSET:
            _CACHE_SUBSET[clave] = _subset_b64(_instanciar(archivo, peso), glifos)
        fuentes.append((fam, peso, estilo, _CACHE_SUBSET[clave]))
    return fuentes


class Medidor:
    """Mide texto: la mono es aritmética, la serif necesita la tabla real."""

    def __init__(self, serif: TTFont):
        self.cmap = serif.getBestCmap()
        self.hmtx = serif["hmtx"]
        self.em = serif["head"].unitsPerEm

    def mono(self, texto: str, tam: float) -> float:
        return len(texto) * AVANCE * tam

    def serif(self, texto: str, tam: float) -> float:
        total = 0
        for ch in texto:
            g = self.cmap.get(ord(ch))
            total += self.hmtx[g][0] if g else self.em * 0.5
        return total * tam / self.em


# ---------------------------------------------------------------- utilidades

def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def envolver(texto: str, tam: float, ancho_max: float) -> list[str]:
    """Corta en líneas que entren en ancho_max (monoespaciada)."""
    cupo = max(10, int(ancho_max / (AVANCE * tam)))
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        tentativa = (actual + " " + p).strip()
        if len(tentativa) <= cupo:
            actual = tentativa
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


class Lienzo:
    """Acumula elementos y lleva la cuenta del alto."""

    def __init__(self):
        self.partes: list[str] = []
        self.y = 0.0
        # que caras y que glifos pide esta banda, para embeber solo eso
        self.usados: dict[tuple[str, int], set[str]] = {}

    def texto(self, x, base, contenido, color, tam=13, peso=400, serif=False,
              ancla="start", subrayado=False):
        fam = "LO" if serif else "FC"
        self.usados.setdefault((fam, peso), set()).update(contenido)
        estilo = "font-style:italic;" if serif else ""
        deco = "text-decoration:underline;" if subrayado else ""
        self.partes.append(
            f'<text x="{x:.1f}" y="{base:.1f}" font-family="{fam}" font-size="{tam}" '
            f'font-weight="{peso}" fill="{color}" text-anchor="{ancla}" '
            f'style="{estilo}{deco}">{esc(contenido)}</text>'
        )

    def rect(self, x, y, w, h, relleno=None, borde=None, rx=0, grosor=1):
        f = f'fill="{relleno}"' if relleno else 'fill="none"'
        s = f' stroke="{borde}" stroke-width="{grosor}"' if borde else ""
        r = f' rx="{rx}"' if rx else ""
        self.partes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{r} {f}{s}/>')

    def circulo(self, cx, cy, r, relleno):
        self.partes.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{relleno}"/>')


# ---------------------------------------------------------------- constantes de maquetación

TAM_TERMINAL = 14      # líneas de prompt
TAM_CUERPO = 13        # prosa y listados
TAM_CHIP = 12          # anotaciones
TAM_NOMBRE = 22        # salida de whoami
TAM_ESPECIE = 17       # nombre científico (serif)
TAM_ARBOL = 15         # el árbol necesita cuerpo mayor con interlineado 100%
ALTO_PROMPT = 28
ALTO_CUERPO = 22
SANGRIA = 40
MARGEN = 26           # aire entre bandas: al apilarse en el README quedaban pegadas
MARGEN_PIE = 10       # respiro al final de cada banda


def prompt(l: Lienzo, comando: str, C: dict, x=0):
    """Dibuja `neo236@pastizal:~$ comando` y devuelve el alto consumido."""
    base = l.y + TAM_TERMINAL * 0.78
    usuario = TEXTO["prompt"]
    l.texto(x, base, usuario, C["texto/etiqueta"], TAM_TERMINAL)
    cx = x + len(usuario) * AVANCE * TAM_TERMINAL + 6
    l.texto(cx, base, ":~$", C["texto/apagado"], TAM_TERMINAL)
    cx += 3 * AVANCE * TAM_TERMINAL + 6
    l.texto(cx, base, comando, C["texto/titulo"], TAM_TERMINAL)
    l.y += ALTO_PROMPT


# ---------------------------------------------------------------- bandas

def banda_cabecera(l: Lienzo, C: dict, M: Medidor):
    c = TEXTO["cabecera"]
    alto_barra = 34
    r = 4.5
    l.partes.append(
        f'<path d="M{r},0 H{ANCHO-r} A{r},{r} 0 0 1 {ANCHO},{r} V{alto_barra} H0 V{r} '
        f'A{r},{r} 0 0 1 {r},0 Z" fill="{C["fondo/barra"]}"/>'
    )
    l.partes.append(
        f'<line x1="0" y1="{alto_barra-0.5}" x2="{ANCHO}" y2="{alto_barra-0.5}" '
        f'stroke="{C["borde/github"]}" stroke-width="1"/>'
    )
    for i, col in enumerate(C["barra/botones"]):
        l.circulo(19.5 + i * 18, alto_barra / 2, 5.5, col)
    l.texto(ANCHO / 2, alto_barra / 2 + TAM_CHIP * 0.35, c["ruta"],
            C["texto/apagado"], TAM_CHIP, ancla="middle")
    l.y = alto_barra + 22

    prompt(l, c["comando"], C)
    base = l.y + TAM_NOMBRE * 0.78
    l.texto(0, base, c["nombre"], C["texto/cuerpo"], TAM_NOMBRE, peso=600)
    l.y += TAM_NOMBRE * 1.5 + 4

    base = l.y + TAM_ESPECIE * 0.78
    x = 0
    l.texto(x, base, c["especie"], C["texto/titulo"], TAM_ESPECIE, serif=True)
    x += M.serif(c["especie"], TAM_ESPECIE) + 10
    l.texto(x, base, c["subespecie"], C["texto/etiqueta"], TAM_ESPECIE, serif=True)
    x += M.serif(c["subespecie"], TAM_ESPECIE) + 10
    l.texto(x, base + 1, c["especimen"], C["texto/apagado"], TAM_CHIP)
    l.y += TAM_ESPECIE * 1.5


def banda_presentacion(l: Lienzo, C: dict, M: Medidor):
    prompt(l, TEXTO["presentacion"]["comando"], C)
    l.y -= 6


def banda_man(l: Lienzo, C: dict, M: Medidor):
    m = TEXTO["man"]
    prompt(l, m["comando"], C)
    l.y += 8

    base = l.y + TAM_CHIP * 0.78
    l.texto(0, base, m["encabezado"], C["texto/apagado"], TAM_CHIP)
    l.texto(ANCHO / 2, base, m["centro"], C["texto/apagado"], TAM_CHIP, ancla="middle")
    l.texto(ANCHO, base, m["encabezado"], C["texto/apagado"], TAM_CHIP, ancla="end")
    l.y += 30

    for sec in m["secciones"]:
        base = l.y + TAM_CUERPO * 0.78
        l.texto(0, base, sec["titulo"], C["texto/etiqueta"], TAM_CUERPO, peso=600)
        l.y += ALTO_CUERPO + 4
        tipo = sec["tipo"]

        if tipo == "definicion":
            base = l.y + TAM_CUERPO * 0.78
            l.texto(SANGRIA, base, sec["clave"], C["texto/titulo"], TAM_CUERPO)
            x = SANGRIA + M.mono(sec["clave"], TAM_CUERPO) + 8
            l.texto(x, base, sec["valor"], C["texto/cuerpo"], TAM_CUERPO)
            l.y += ALTO_CUERPO

        elif tipo == "uso":
            for ln in sec["lineas"]:
                base = l.y + TAM_CUERPO * 0.78
                l.texto(SANGRIA, base, sec["clave"], C["texto/titulo"], TAM_CUERPO)
                x = SANGRIA + M.mono(sec["clave"], TAM_CUERPO) + 8
                l.texto(x, base, ln, C["texto/apagado"], TAM_CUERPO)
                l.y += ALTO_CUERPO

        elif tipo in ("prosa", "apagado"):
            color = C["texto/apagado"] if tipo == "apagado" else C["texto/cuerpo"]
            for p in sec["parrafos"]:
                for ln in envolver(p, TAM_CUERPO, PROSA_MAX):
                    l.texto(SANGRIA, l.y + TAM_CUERPO * 0.78, ln, color, TAM_CUERPO)
                    l.y += ALTO_CUERPO
                l.y += 6
            l.y -= 6

        elif tipo == "variables":
            for clave, valor in sec["filas"]:
                base = l.y + TAM_CUERPO * 0.78
                l.texto(SANGRIA, base, clave, C["texto/etiqueta"], TAM_CUERPO)
                l.texto(SANGRIA + 150, base, valor, C["texto/cuerpo"], TAM_CUERPO)
                l.y += ALTO_CUERPO

        l.y += 16
    l.y -= 16


def banda_procesos(l: Lienzo, C: dict, M: Medidor):
    p = TEXTO["procesos"]
    prompt(l, p["comando"], C)
    l.y += 8
    for pid, proyecto, resto in p["filas"]:
        base = l.y + TAM_CUERPO * 0.78
        l.texto(0, base, pid, C["texto/etiqueta"], TAM_CUERPO)
        x = M.mono(pid, TAM_CUERPO) + 10
        l.texto(x, base, proyecto, C["texto/titulo"], TAM_CUERPO)
        x += M.mono(proyecto, TAM_CUERPO) + 10
        l.texto(x, base, resto, C["texto/cuerpo"], TAM_CUERPO)
        l.y += ALTO_CUERPO


def banda_destacado(l: Lienzo, C: dict, M: Medidor):
    d = TEXTO["destacado"]
    prompt(l, d["comando"], C)
    l.y += 8
    base = l.y + TAM_CUERPO * 0.78
    x = 0
    for txt, col in [("commit", C["texto/apagado"]), (d["hash"], C["texto/cuerpo"]),
                     (d["ref"], C["texto/apagado"]), (d["tag"], C["texto/etiqueta"])]:
        l.texto(x, base, txt, col, TAM_CUERPO)
        x += M.mono(txt, TAM_CUERPO) + 8
    l.y += ALTO_CUERPO + 12

    tope = l.y
    sang = 26
    base = l.y + 17 * 0.78
    l.texto(sang, base, d["titulo"], C["texto/titulo"], 17, peso=600)
    l.y += 17 * 1.4 + 6
    for ln in envolver(d["descripcion"], TAM_CUERPO, PROSA_MAX):
        l.texto(sang, l.y + TAM_CUERPO * 0.78, ln, C["texto/cuerpo"], TAM_CUERPO)
        l.y += ALTO_CUERPO
    l.y += 6
    l.texto(sang, l.y + TAM_CUERPO * 0.78, d["repo"], C["texto/etiqueta"],
            TAM_CUERPO, subrayado=True)
    l.y += ALTO_CUERPO
    # filete a la izquierda, como el cuerpo de un commit en git show
    l.partes.insert(0, f'<rect x="0" y="{tope:.1f}" width="2" '
                       f'height="{l.y - tope:.1f}" fill="{C["acento/rufo"]}"/>')


def banda_stack(l: Lienzo, C: dict, M: Medidor):
    s = TEXTO["stack"]
    prompt(l, s["comando"], C)
    l.y += 10
    nivel = {0: C["texto/cuerpo"], 1: C["texto/etiqueta"], 2: C["texto/titulo"]}
    for pre, nombre, contenido, niv in s["filas"]:
        base = l.y + TAM_ARBOL * 0.78
        x = 0
        if pre:
            l.texto(x, base, pre, C["texto/apagado"], TAM_ARBOL)
            x += M.mono(pre, TAM_ARBOL)
        l.texto(x, base, nombre, nivel[niv], TAM_ARBOL)
        if contenido:
            l.texto(270, base, contenido, C["texto/cuerpo"], TAM_ARBOL)
        l.y += TAM_ARBOL       # interlineado 100%: los glifos de caja se tocan


def banda_huellas(l: Lienzo, C: dict, M: Medidor):
    prompt(l, TEXTO["huellas"]["comando"], C)
    l.y -= 6


def banda_cierre(l: Lienzo, C: dict, M: Medidor):
    c = TEXTO["cierre"]
    tam = 13
    partes = [(c["izquierda"], C["texto/apagado"]), (c["centro"], C["texto/titulo"]),
              (c["derecha"], C["texto/apagado"])]
    total = sum(M.serif(t, tam) for t, _ in partes) + 14
    x = (ANCHO - total) / 2
    base = l.y + tam * 0.78
    for t, col in partes:
        l.texto(x, base, t, col, tam, serif=True)
        x += M.serif(t, tam) + 7
    l.y += tam * 1.6


def banda_pastizal(l: Lienzo, C: dict, M: Medidor, claro=False):
    tonos = TOKENS["pastizal"]["tonos_claro" if claro else "tonos"]
    alto, px, paso = 28, 3, 6

    def rnd(s):
        return abs(math.sin(s) * 43758.5453) % 1

    tope = l.y
    for x in range(0, ANCHO, paso):
        h = 10 + int(rnd(x * 12.9898) * 17)
        l.rect(x, tope + alto - h, px, h, relleno=tonos[int(rnd(x * 78.233) * len(tonos))])
    l.y += alto


BANDAS = {
    "cabecera": banda_cabecera,
    "presentacion": banda_presentacion,
    "man": banda_man,
    "procesos": banda_procesos,
    "destacado": banda_destacado,
    "stack": banda_stack,
    "huellas": banda_huellas,
    "cierre": banda_cierre,
    "pastizal": banda_pastizal,
}


# ---------------------------------------------------------------- ensamblado

def envolver_svg(lienzo: Lienzo, alto: float, fuentes, titulo: str) -> str:
    caras = "".join(
        f"@font-face{{font-family:'{fam}';"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
        f"font-weight:{peso};font-style:{estilo};font-display:block}}"
        for fam, peso, estilo, b64 in fuentes
    )
    cuerpo = "".join(lienzo.partes)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" '
        f'height="{alto:.0f}" viewBox="0 0 {ANCHO} {alto:.0f}" '
        f'role="img" aria-label="{esc(titulo)}">'
        f"<style>{caras}text{{white-space:pre}}</style>{cuerpo}</svg>"
    )


def main():
    medidor = Medidor(TTFont(RAIZ / "fuentes" / "Lora-Italic.ttf"))

    SALIDA.mkdir(parents=True, exist_ok=True)
    resumen = []
    for nombre, fn in BANDAS.items():
        for modo in ("oscuro", "claro"):
            C = TOKENS[modo]
            l = Lienzo()
            # la cabecera arranca pegada arriba; las demas bandas llevan aire
            if nombre != "cabecera":
                l.y = MARGEN
            if nombre == "pastizal":
                fn(l, C, medidor, claro=(modo == "claro"))
            else:
                fn(l, C, medidor)
            l.y += MARGEN_PIE
            svg = envolver_svg(l, math.ceil(l.y), _fuentes_para(l), nombre)
            sufijo = "dark" if modo == "oscuro" else "light"
            (SALIDA / f"{nombre}-{sufijo}.svg").write_text(svg, encoding="utf-8")
            if modo == "oscuro":
                resumen.append((nombre, int(l.y), len(svg) // 1024))

    version = str(TOKENS.get("version_bandas", 1))
    contenido_readme = armador.construir(TEXTO, version, TOKENS["oscuro"], TOKENS["claro"], TOKENS["rampa_lenguajes"])
    (RAIZ.parent / "README.md").write_text(contenido_readme, encoding="utf-8", newline="")
    print(f"  README.md reescrito (bandas v{version})")
    print()

    print(f"  {'banda':14}{'alto':>7}{'KB':>7}")
    for n, alto, kb in resumen:
        print(f"  {n:14}{alto:>7}{kb:>7}")
    print(f"  {'TOTAL':14}{sum(r[1] for r in resumen):>7}")


if __name__ == "__main__":
    main()
