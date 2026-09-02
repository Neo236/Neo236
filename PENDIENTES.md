# Pendientes

Lo que queda por hacer, con el contexto para poder retomarlo sin volver a
investigar. Ver [render/README.md](render/README.md) para cómo funciona el
generador y [CREDITOS.md](CREDITOS.md) para lo ajeno.

---

## 1. Sacar piezas de Vercel haciéndolas estáticas

**El cambio con más impacto de la lista.** Hoy 4 de las 7 piezas del perfil
dependen de Vercel en cada visita. Tres de esas cuatro no tienen por qué ser un
servicio en vivo.

### 1a. El typing

Es **100 % determinista**: frases fijas, colores fijos, tiempos fijos. Cada
visita paga Vercel, una función y **dos llamadas a Google Fonts** para producir
siempre exactamente el mismo archivo.

Generarlo con el pipeline de Python que ya hace las bandas daría:

- Vercel fuera del camino para esa pieza
- **Google Fonts eliminado del todo** — el pipeline ya subsetea y embebe Fira
  Code, y lo haría mejor: solo los caracteres de las 21 frases, así que
  probablemente pese menos que los 88 KB actuales
- Reproducible y versionado como el resto, con el mismo `SOURCE_DATE_EPOCH`
- Un repo y un proyecto de Vercel menos

Estimado: ~80 líneas en `render.py`. La estructura SMIL está documentada en
`MODIFICACIONES.md` del fork `readme-typing-svg`.

### 1b. Las tarjetas de stats y lenguajes

Cambian como mucho una vez por día. Podrían generarse en el Action y publicarse
en la rama `output`, **exactamente como ya se hace con la snake y la racha**.
Saca Vercel y la API de GitHub del camino de render: la de stats pasaría de
~3.2 s a ~0.2 s.

### 1c. Lo que sí necesita seguir vivo

Solo **Spotify**: "qué estoy escuchando ahora" es inherentemente en tiempo real.

> **Sobre self-hostear en OCI:** es viable (hay tenancy con `prod`, `sandbox` y
> `shared-network`), pero conviene hacer 1a y 1b **primero**. Bajar de 4
> servicios a 1 sin agregar una máquina que mantener es mejor que mover los 4 a
> una VM: Vercel aporta CDN global, TLS y despliegue automático que habría que
> reponer. Si después de eso querés self-hostear el de Spotify —la única pieza
> que queda—, es una app Flask chica y tiene sentido.

---

## 2. Contenido desactualizado

La tarjeta muestra **Rust como 3er lenguaje (18.85 %)** y Rust no aparece ni en
el `tree ~/stack` ni en el `man`. Igual **Dart** (2.84 %) y **Astro** (2.79 %).

Hace falta decidir qué decir de cada uno antes de escribirlo — no se puede
inventar. Editar en `render/contenido.yml`.

Al revés, **Python está en el stack pero no en la tarjeta** porque vive en repos
privados: eso se arregla con el punto 4.

---

## 3. Peso de la tarjeta de stats

Es el 55 % del peso de la página. Ya no rompe la maquetación (todas las imágenes
declaran `width` y `height`), así que esto es opcional.

| | cuadros | fps | peso |
|---|---|---|---|
| como está | 91 | 10 | 267 KB |
| 1 de cada 2 | 46 | 5 | 133 KB |
| 1 de cada 3 | 31 | 3 | 89 KB |

El GIF ya está optimizado en paleta (reencodearlo a 128 colores ahorra 4 KB): el
peso son los cuadros. **Es arte propio, decisión de Lautaro.**

Aparte, `include_all_commits=true` agrega ~1.5 s porque llama a la API de
búsqueda de GitHub. Sacarlo lo baja a la mitad, pero el número de commits pasa a
contar solo el último año.

---

## 4. Credenciales

Ninguna está en el código: **se escaneó el historial de los cuatro repos y no hay
un solo secreto versionado**. Todas viven en variables de entorno de Vercel o en
Firestore.

| Credencial | Dónde | Estado |
|---|---|---|
| `PAT_1` | Vercel · `github-readme-stats` | Solo alcance público. **Ver abajo** |
| `SPOTIFY_CLIENT_ID` | Vercel · `spotify-github-profile` | No es secreto |
| `SPOTIFY_SECRET_ID` | Vercel · `spotify-github-profile` | Secreto |
| `FIREBASE` | Vercel · `spotify-github-profile` | Secreto (service account) |
| `BASE_URL` | Vercel · `spotify-github-profile` | No es secreto. **Tiene que incluir `https://`** o Spotify responde `redirect_uri: Unsafe` |
| refresh token de Spotify | Firestore, `users/{uid}` | Reglas en `allow read, write: if false`: solo el Admin SDK entra |
| `GITHUB_TOKEN` | GitHub Actions | Automático por corrida, alcance `contents: write` |
| `typing-aguara` | — | **No usa ninguna.** Es apátrida |

### Para revisar

- **Vencimiento del `PAT_1`.** Si se creó "sin vencimiento", conviene ponerle uno
  y anotar la fecha. Si vence sin que nadie lo note, las dos tarjetas se caen.
- **La service account de Firebase no rota sola.** Las claves de service account
  no vencen: si se filtra, sirve para siempre hasta que se revoque a mano.
- **El refresh token de Spotify no vence** pero se puede revocar desde
  spotify.com/account/apps. Si alguna vez la tarjeta queda en "fuera de línea"
  para siempre, mirar ahí primero.

### Ampliar el `PAT_1` a repos privados

Para que aparezcan **TypeScript y Python**, que son los lenguajes reales pero
viven en repos privados. La consulta de `top-languages` no filtra por privacidad,
así que alcanza con ampliar el alcance del token:

1. GitHub → Settings → Developer settings → Personal access tokens (classic),
   con scope `repo`.
2. Vercel → proyecto `github-readme-stats` → Settings → Environment Variables →
   editar `PAT_1` (ya existe; le falta el alcance).
3. Redeploy.

> Ojo: eso **publica los porcentajes de lenguaje de los repos privados**. Los
> nombres no se exponen, pero la barra refleja trabajo privado. Un token
> *fine-grained* de solo lectura sobre repos elegidos da el mismo efecto con
> menos alcance.

---

## 5. Accesibilidad

- **La snake es una animación en bucle sin forma de pausarla**, igual que lo era
  el typing: el caso de WCAG 2.2.2. El typing ya tiene fallback bajo
  `prefers-reduced-motion`; la snake no. Se inyecta CSS en `snake.yml`, así que
  se puede resolver ahí — la animación de snk es CSS, no SMIL, o sea que
  `animation: none` bajo esa media query alcanza.
- **Los `alt` son más cortos que el contenido.** El `man` dibuja 885 caracteres
  de texto y su `alt` tiene 251. Un lector de pantalla recibe un resumen, no el
  contenido. Es el costo de que el README sea imágenes; no tiene arreglo dentro
  de este diseño.

---

## 6. Cabos sueltos

- **Figma quedó desincronizado.** Se editaron directo en `tokens.json` las dos
  rampas de lenguajes, el rufo claro (`#B04D19`), `fondo/github` claro
  (`#FFFFFF`) y `barra/botones`. El conector necesita autorización OAuth.
- **`Neo236/github-readme-streak-stats@main` no está fijado al SHA.** Es fork
  propio, así que el riesgo es menor, pero corre con `contents: write`.
- **`Neo236/snk` no se usa** — la inyección de CSS resolvió sin forkearlo. Se
  puede borrar.
- **El proyecto viejo `readme-typing-svg` en Vercel** quedó en pie por si había
  que volver. Si `typing-aguara` viene bien, se puede borrar.
