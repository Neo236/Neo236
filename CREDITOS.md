# Créditos y atribuciones

Este perfil se apoya en varios proyectos de código abierto. Acá está cada uno: quién lo hizo,
bajo qué licencia, y **exactamente qué hicimos con él** — porque no es lo mismo integrar algo
tal cual que modificarlo.

## Resumen

| Proyecto | Autoría | Licencia | Qué hacemos con él |
|---|---|---|---|
| [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) | Anurag Hazra | MIT | **Fork modificado**, self-hosteado |
| [spotify-github-profile](https://github.com/kittinan/spotify-github-profile) | Kittinan Wangthammang | MIT | **Fork modificado**, self-hosteado |
| [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) | Jonah Lawrence (DenverCoder1) | MIT | **Fork modificado**, self-hosteado |
| [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) | Jonah Lawrence (DenverCoder1) | MIT | Fork **sin modificar**, usado como GitHub Action |
| [snk](https://github.com/Platane/snk) | Platane | *sin licencia declarada* | Action publicada, **sin modificar** su código |
| [Fira Code](https://github.com/tonsky/FiraCode) | Nikita Prokopov | SIL OFL 1.1 | Tipografía, **subseteada y embebida** en las bandas y en el typing |
| [Lora](https://github.com/cyrealtype/Lora-Cyrillic) | Cyreal | SIL OFL 1.1 | Tipografía del nombre científico, **subseteada y embebida** |
| [Google Fonts](https://fonts.google.com) | Google | servicio | El typing le pide Fira Code **en cada request** |

Los cuatro forks conservan intacto el archivo `LICENSE` original, como exige la licencia MIT.

Las dos tipografías son **SIL OFL 1.1**, que permite embeberlas pero pide atribución: por eso
figuran acá y no solo en el código. Se embeben subconjuntos, no la fuente completa, y no se
venden ni se redistribuyen por separado.

## Qué modificamos en cada fork

### github-readme-stats → [`Neo236/github-readme-stats`](https://github.com/Neo236/github-readme-stats)
Genera las tarjetas de estadísticas y de lenguajes.
- Se agregaron los temas `aguara` y `aguara_light` con la paleta del proyecto.
- El círculo de rango se reemplazó por un GIF recortado en círculo con un aro del color del tema.
- Se agregó el parámetro `card_height` a la tarjeta de lenguajes, para poder igualar alturas.
- Se bajó el ancho mínimo de la tarjeta con rango, para que entre en el ancho real del README.
- Se agregó el parámetro `lang_palette`, que reasigna los colores de los lenguajes
  interpolando una rampa propia en orden de uso, en vez de usar los colores oficiales de
  GitHub — que eran lo único del perfil que ignoraba la paleta.
- Se acortaron etiquetas en español que chocaban con su valor.
- Se subió el contraste del título en el tema claro para cumplir 4.5:1 sobre el fondo de la
  propia tarjeta.

  El detalle está en [`MODIFICACIONES.md`](https://github.com/Neo236/github-readme-stats/blob/master/MODIFICACIONES.md) del fork.

### spotify-github-profile → [`Neo236/spotify-github-profile`](https://github.com/Neo236/spotify-github-profile)
Muestra qué estoy escuchando.
- **Corrección de comportamiento:** Spotify devuelve el último tema aunque esté pausado; ahora
  solo cuenta como "reproduciendo" si `is_playing` es verdadero.
- Se agregó un estado *fuera de línea* propio, con ilustración y texto en capas.
- El tema `spotify-embed` se recoloreó a la paleta del proyecto.
- Se cambió el tamaño de la tarjeta al ancho real del README.

### readme-typing-svg → [`Neo236/readme-typing-svg`](https://github.com/Neo236/readme-typing-svg)
La línea de texto que se escribe sola en la cabecera.
- Se reescribió la animación para que se comporte como una terminal: velocidad de tipeo
  constante, revelado y cursor **paso a paso por carácter**, y cursor sólido mientras se
  escribe que parpadea solo cuando está esperando.
- Se corrigió que el padding se contara dos veces, lo que cortaba los últimos dos caracteres
  de cada frase.
- Se agregaron los parámetros `padding`, `borderColor`, `borderRadius` y `restPause`.
- Se agregó una línea quieta bajo `prefers-reduced-motion`, porque es una animación en bucle
  sin forma de pausarla (WCAG 2.2.2).
- Se agregó configuración de despliegue para Vercel y se corrigió la resolución del autoload.

  El detalle está en [`MODIFICACIONES.md`](https://github.com/Neo236/readme-typing-svg/blob/main/MODIFICACIONES.md) del fork.

### github-readme-streak-stats → [`Neo236/github-readme-streak-stats`](https://github.com/Neo236/github-readme-streak-stats)
La racha de contribuciones. **No se modificó el código.** Se usa como GitHub Action para generar
un SVG estático dentro de este repo, en vez de enlazar el servicio público — que respondió
503, 403 y 504 en distintos momentos y rompía la tarjeta. El propio autor recomienda esta vía.

### snk → [`Platane/snk`](https://github.com/Platane/snk)
La serpiente que se come las contribuciones. **No modificamos su código:** se usa la Action
publicada, que es su uso previsto. Los colores de la crin y la punta de la cola se logran
**post-procesando el SVG que genera**, dentro de nuestro propio workflow.

> ⚠️ Este proyecto **no declara licencia**. Sin licencia, por defecto se reservan todos los
> derechos. Por eso nos limitamos a consumirlo como Action pública y no redistribuimos su código.

## Medios

- La ilustración del anillo de rango proviene de material de **PBS Nature**. Se usa de forma
  decorativa en un perfil personal sin fin comercial; **no está licenciada para redistribución**.
- La fotografía del estado *fuera de línea* es de origen no verificado.

Ambas piezas están señaladas para reemplazarse por arte propio.

## Sobre este perfil

El diseño, la paleta, los textos y las modificaciones descritas arriba son propios.
Si algo de acá te sirve, tomalo — y si podés, dale crédito a los autores originales de la tabla.
