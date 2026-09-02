# Generador del perfil

El README del perfil **no se edita a mano**. Se genera:

```bash
py -3.13 render/src/render.py
```

Eso reescribe las 18 bandas SVG de `assets/bandas/` (9 secciones × 2 modos) y el
`README.md` de la raíz. Si editás el README a mano, el próximo `render.py` lo pisa.

## Qué archivo toca cuál cosa

| Querés cambiar | Editá |
|---|---|
| Un texto, una frase del typing, una URL de tarjeta | `render/contenido.yml` |
| Un color, una rampa, una medida | `render/tokens.json` |
| Cómo se dibuja una banda | `render/src/render.py` |
| Cómo se arma el markdown | `render/src/readme.py` |
| El recorte y los colores de la snake | `.github/workflows/snake.yml` |

## Cosas que no son obvias

**Las bandas no llevan fondo.** Se apoyan sobre el fondo real de GitHub, que es
`#0D1117` en oscuro y **`#FFFFFF` en claro** (medido, no supuesto). Por eso los
contrastes de las bandas se auditan contra esos dos y no contra los tokens de
fondo, que son para las tarjetas.

**El ancho real es 831 px.** No 880, no 900. Es el ancho del área de contenido de
un README de GitHub. Las tarjetas van a 411 para que entren dos por fila.

**Cada banda embebe solo la fuente que usa.** `Lienzo` anota qué caras y qué
glifos pide mientras dibuja, y `_fuentes_para()` subsetea exactamente eso. Antes
se embebía el mismo blob de 26.8 KB en las nueve: la fuente era el 88 % del peso.
Si agregás un carácter nuevo a una banda, se incluye solo; no hay lista que
mantener.

**El generador es reproducible.** `SOURCE_DATE_EPOCH=0` se fija en `render.py`
antes de usar fontTools, que si no estampa la hora actual en cada subset y dos
corridas seguidas dan bytes distintos. Dos corridas deben dar el mismo sha256:

```bash
py -3.13 render/src/render.py && sha256sum assets/bandas/*.svg > /tmp/a
py -3.13 render/src/render.py && sha256sum assets/bandas/*.svg | diff /tmp/a -
```

**Todas las imágenes llevan `width` y `height`.** Siempre los dos: con uno solo el
navegador no deduce la relación de aspecto y el hueco vale 0 px hasta que la
imagen carga, así que la grilla salta. Los altos de las bandas salen del propio
generador; los de las piezas vivas, de `contenido.yml → vivas.medidas`.

**Las comas en una URL van como `%2C`.** Dentro de un `srcset`, una coma cruda
parte la URL en varios candidatos y GitHub sirve un recorte roto.

**El `v=` del typing es solo para romper caché.** GitHub cachea las imágenes por
camo usando la URL como clave, así que un cambio en la plantilla del fork no se
ve hasta que cambie la URL. Subilo cada vez que toques `readme-typing-svg`.

## Dónde vive cada pieza

Ver [CREDITOS.md](../CREDITOS.md) para el detalle de qué es ajeno y qué se
modificó. Resumen de hosting:

- **Bandas, snake y racha**: `raw.githubusercontent`, sin terceros al renderizar.
- **typing**: Vercel (`typing-aguara`) — y llama a **Google Fonts en cada
  request**. Si Google no responde, cae a `monospace` genérica.
- **stats y lenguajes**: Vercel (`readmestats.neo236.fun`) + API de GitHub.
- **spotify**: Vercel (`spotify-gh.neo236.fun`) + API de Spotify + Firestore.
