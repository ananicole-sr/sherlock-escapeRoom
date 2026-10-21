# Etapa 6: comparación y análisis

Este análisis usa solo resultados guardados:

| Archivo | Contenido |
|---|---|
| `data/evaluation_results.json` | 60 ejecuciones: 20 preguntas × KMP, Z-function y búsqueda aproximada, con filtro del relato de cada pregunta, top_k = 5 y una respuesta nueva de Qwen2.5-0.5B-Instruct por ejecución |
| `data/scaling_results.json` y `data/scaling_summary.csv` | Experimento de tamaño de colección: 180 mediciones, sin Qwen |
| `reports/evaluation_review.json` | Revisión de calidad, versión 2. **Valoraciones preliminares hechas por IA, pendientes de validación humana** |

Las gráficas se generan con `make_stage6_figures.py` y los números que las respaldan están en
`reports/figures/stage6_numbers.json`.

## Condiciones de medición

- Un solo equipo (CPU AMD Ryzen 5 4600H) con Python 3.12; los tiempos dependen de esta máquina y de esta
  implementación en Python.
- **Búsqueda:** 1 calentamiento y 5 repeticiones medidas por pregunta y motor. Se reporta el tiempo que mide
  el propio motor (`retrieval_time_ms`), desde que procesa la pregunta hasta que entrega el ranking. Las
  5 repeticiones devolvieron siempre el mismo ranking.
- **Generación:** se mide aparte, y nunca se suma al tiempo de búsqueda.
- **Caché:** la búsqueda exacta no tiene. La búsqueda aproximada guarda los n-gramas de caracteres de cada
  fragmento; en la evaluación de 60 ejecuciones se calculan en el calentamiento, y en el experimento de
  tamaño se calculan durante la preparación, fuera del tiempo medido. Levenshtein no tiene caché y siempre
  corre dentro del tiempo medido.
- **Tamaño de la muestra:** son 20 preguntas y 3 relatos (147 fragmentos). Es una colección pequeña: los
  resultados describen estas mediciones y no permiten generalizar qué motor es más rápido en cualquier
  colección.

## 1. Eficiencia en las 60 ejecuciones

| Motor | Búsqueda: media | Mediana | Mín.–máx. | Generación: media | Mediana | Candidatos | Examinados | Encontrados | Devueltos | Evidencia recuperada |
|---|---|---|---|---|---|---|---|---|---|---|
| KMP | 41.1 ms | 34.2 ms | 5.3–107.2 ms | 6.56 s | 5.81 s | 42.5 | 23.5 | 23.5 | 5.0 | 12/17 |
| Z-function | 48.9 ms | 40.4 ms | 6.3–124.7 ms | 6.83 s | 5.74 s | 42.5 | 23.5 | 23.5 | 5.0 | 12/17 |
| Aproximada | 22.6 ms | 2.5 ms | 1.4–70.3 ms | 6.29 s | 6.08 s | 147.0 | 49.0 | 48.6 | 5.0 | 13/17 |

Las cantidades de fragmentos son medias por pregunta:

- **Candidatos:** en la búsqueda exacta, los fragmentos que propone el índice invertido, de cualquier relato.
  En la búsqueda aproximada, toda la colección.
- **Examinados:** los que realmente se recorren con KMP o Z, o que se puntúan en la búsqueda aproximada,
  después del filtro de relato.
- **Encontrados:** los fragmentos con al menos una coincidencia exacta, o con puntuación mayor que 0 en la
  búsqueda aproximada, antes de aplicar `top_k`.
- **Devueltos:** los que quedan después de aplicar `top_k`.

![Tiempo de búsqueda por pregunta](figures/fig1_retrieval_time.png)

**Qué muestra:** el tiempo de búsqueda de cada una de las 20 preguntas, por motor, con su media (línea
continua) y su mediana (línea punteada).

**Qué se observa:**
- La búsqueda aproximada tiene la media más baja (22.6 ms) y una mediana muy baja (2.5 ms), pero se reparte
  en dos grupos.
- Las preguntas en las que Levenshtein corrige algún término tardan entre 35 y 70 ms; las demás, entre 1 y
  3 ms. En las preguntas con errores de escritura, la búsqueda aproximada promedió 56.9 ms y KMP 36.8 ms.
- KMP fue más rápido que la búsqueda aproximada en 8 de las 20 preguntas.
- Z fue más lento que KMP en las 20 preguntas, examinando exactamente los mismos fragmentos.

**Limitaciones:** es una sola implementación en Python sobre una colección pequeña. Una explicación posible
para la diferencia entre KMP y Z es que esta implementación de Z construye un arreglo sobre patrón +
separador + texto por cada fragmento y término, pero no se midió por separado.

![Tiempo de generación](figures/fig2_generation_time.png)

**Qué muestra:** el tiempo que tardó Qwen en generar cada respuesta, medido aparte de la búsqueda.

**Qué se observa:**
- La generación tardó entre 56 y 5,284 veces más que la búsqueda (mediana: 172 veces), y la búsqueda nunca
  pasó del 1.7 % del tiempo total.
- Las medias por motor son parecidas (6.3–6.8 s). Los valores extremos (19.5 y 23.5 s) son RH06 con KMP y
  con Z, donde el modelo produjo una respuesta larga que copia frases del contexto.

**Limitaciones:** hay una sola generación por combinación; no se midió la variabilidad de la generación.

![Fragmentos por consulta](figures/fig3_chunk_counts.png)

**Qué muestra:** cuántos fragmentos maneja cada motor por consulta, con el filtro de relato activado.

**Qué se observa:** la búsqueda exacta parte de 42.5 candidatos del índice y examina 23.5 del relato. La
búsqueda aproximada puntúa los 49 fragmentos del relato. Su conteo de "encontrados" (48.6) casi no filtra,
porque los n-gramas de caracteres le dan una puntuación pequeña a casi cualquier fragmento.

**Limitaciones:** "encontrados" no significa lo mismo en los dos motores: en la búsqueda exacta es una
coincidencia literal, y en la aproximada es una puntuación mayor que cero. Por eso no conviene compararlos
como si midieran lo mismo.

## 2. Tamaño de la colección

Se construyeron subcolecciones reales de 1, 2 y 3 relatos. Cada una tiene su propio índice invertido,
vocabulario, frecuencias, tokens de contenido y n-gramas, y su preparación se midió por separado: entre 12 y
42 ms. No se usó filtro de relato. Hay tres órdenes de crecimiento, y cada uno usa las preguntas de su relato
base, que está presente desde la colección de un relato:

| Orden | 1 relato | 2 relatos | 3 relatos | Preguntas |
|---|---|---|---|---|
| A | Speckled Band (54 fragmentos, 52,644 caracteres) | + Blue Carbuncle (97; 94,501) | + Red-Headed League (147; 143,485) | SB01–SB07 |
| B | Blue Carbuncle (43; 41,857) | + Red-Headed League (93; 90,841) | + Speckled Band (147; 143,485) | BC01–BC07 |
| C | Red-Headed League (50; 48,984) | + Speckled Band (104; 101,628) | + Blue Carbuncle (147; 143,485) | RH01–RH06 |

Con tres relatos, los resultados de la subcolección coinciden con los de la colección de producción sin
filtro en 60 de 60 casos.

**Tiempo medio de búsqueda (ms, media sobre las preguntas de cada orden):**

| Orden | Motor | 1 relato | 2 relatos | 3 relatos |
|---|---|---|---|---|
| A | KMP | 79.5 | 66.1 | 84.0 |
| A | Z | 91.7 | 77.8 | 98.2 |
| A | Aproximada | 28.2 | 24.3 | 29.4 |
| B | KMP | 34.2 | 52.6 | 66.7 |
| B | Z | 39.7 | 61.8 | 77.6 |
| B | Aproximada | 15.6 | 17.6 | 25.1 |
| C | KMP | 40.3 | 58.3 | 74.5 |
| C | Z | 46.7 | 68.4 | 88.9 |
| C | Aproximada | 17.0 | 21.9 | 26.3 |

![Tiempo frente al tamaño](figures/fig4_scaling_time.png)

**Qué muestra:** el tiempo medio de búsqueda según el número real de fragmentos de la colección, para los
tres órdenes de crecimiento.

**Qué se observa:**
- En los órdenes B y C los tres motores tardan más a medida que crece la colección.
- En el orden A, el tiempo baja de 1 a 2 relatos y sube de 2 a 3.
- En estas mediciones, sin filtro de relato, la búsqueda aproximada tuvo la media más baja en los tres
  tamaños y los tres órdenes.

**Limitaciones:** son solo tres tamaños y 6 o 7 preguntas por orden. La forma de la curva no demuestra una
ley de crecimiento, y el caso del orden A muestra que el promedio depende de qué preguntas y qué palabras
contiene cada relato.

![Fragmentos examinados frente al tamaño](figures/fig5_scaling_examined.png)

**Qué muestra:** cuántos fragmentos examina cada motor según el tamaño de la colección.

**Qué se observa:**
- La búsqueda aproximada examina siempre toda la colección.
- La búsqueda exacta examina solo los candidatos del índice: de 28.4 a 47.4 fragmentos en el orden A, de
  18.3 a 34.7 en el B y de 23.8 a 45.7 en el C. KMP y Z examinan exactamente los mismos.

**Limitaciones:** examinar menos fragmentos no implica tardar menos. Cada fragmento examinado por KMP o Z
se recorre carácter por carácter en Python, una vez por término; la búsqueda aproximada hace sobre todo
operaciones de conjuntos.

![Efecto de Levenshtein](figures/fig6_levenshtein_effect.png)

**Qué muestra:** el tiempo de la búsqueda aproximada según el tamaño de la colección, separando las
consultas que necesitaron corregir algún término de las que no.

**Qué se observa:**
- Las consultas que necesitaron corrección tardaron entre 14 y 73 ms; las demás, entre 2 y 17 ms.
- Al crecer la colección hay **menos** términos que corregir. Con un solo relato, Levenshtein cambió `lead`
  → `led` y `colour` → `coloured` (orden A), `fight` → `flight` (orden B) y `paid` → `pain` (orden C),
  porque esas palabras no estaban en el vocabulario de ese relato. Con tres relatos ya no las corrige. Pero
  cada corrección que sí hace es **más cara**, porque recorre un vocabulario mayor.
- Que la corrección dependa del vocabulario también significa que, con un solo relato, puede cambiar
  palabras bien escritas (`paid` → `pain`).
- Por eso la media de este motor combina dos efectos opuestos.

**Limitaciones:** esta separación es una observación sobre estas consultas. No se midió por separado el
tiempo de Levenshtein en el experimento de tamaño, aunque la búsqueda sí lo reporta en la evaluación
(`correction_time_ms`).

## 3. Calidad del contexto y de las respuestas

> **Valoraciones preliminares hechas por IA, pendientes de validación humana.** Se basan en
> `reports/evaluation_review.json` (versión 2). Las correcciones respecto a la versión 1 están documentadas
> en `reports/evaluation_review_corrections.md`.

| Motor | Contexto suficiente | Correcta | Parcial | Incorrecta | Abstención apropiada | Abstención no válida | Respaldo completo | Respaldo parcial | Sin respaldo |
|---|---|---|---|---|---|---|---|---|---|
| KMP | 13/20 | 6 | 4 | 9 | 1 | 0 | 9 | 5 | 6 |
| Z-function | 13/20 | 6 | 4 | 9 | 1 | 0 | 9 | 5 | 6 |
| Aproximada | 14/20 | 8 | 4 | 7 | 0 | 1 | 9 | 5 | 6 |

![Calidad preliminar](figures/fig7_quality_preliminary.png)

**Qué muestra:** tres valoraciones de cada una de las 60 respuestas:
- si el contexto que recibió Watson permitía responder;
- si la respuesta es correcta según el relato;
- si lo que afirma está respaldado por el contexto que recibió.

**Qué se observa:**
- La búsqueda aproximada tuvo dos respuestas correctas más que KMP y Z (8 contra 6), un contexto suficiente
  más (14 contra 13) y dos respuestas incorrectas menos (7 contra 9).
- En respaldo, los tres motores tienen la misma distribución.

**Limitaciones:** son 20 preguntas y un solo revisor, que es una IA. Una diferencia de una o dos
respuestas no basta para afirmar que una estrategia es mejor en general.

### Qué estrategia recuperó contexto más útil

- **Observación:** la búsqueda aproximada recuperó la evidencia en 13 de las 17 preguntas respondibles,
  contra 12 de KMP y de Z. La única pregunta donde la recuperó y la búsqueda exacta no fue **RH04**
  ("Why did Holmes beat the pavment with his stik?").
  - **Posible explicación:** Levenshtein corrigió `pavment` → `pavement` y `stik` → `stick`, y entonces
    entró el fragmento 048, que contiene "I was ascertaining whether the cellar stretched out in front or
    behind". La búsqueda exacta buscó los términos tal como estaban escritos y no los encontró en el índice.
- **Las dos estrategias fallaron por igual** en SB03 (el plato de leche sobre la caja fuerte), SB05 (los
  animales, aunque la búsqueda aproximada corrigió `animls` y `roylot`), RH02 y RH03. En RH03 la evidencia
  responde con otras palabras que la pregunta ("to get this not over-bright pawnbroker out of the way").
  En RH02 el fragmento de la cita guardada no llegó, pero el contexto sí era suficiente (fragmento 045).

### Casos con resultados similares

- **KMP y Z-function fueron idénticos en las 20 preguntas:** el mismo contexto carácter por carácter y la
  misma respuesta. Los dos algoritmos encuentran las mismas coincidencias; solo cambia el tiempo.
- **Las tres estrategias dieron exactamente la misma respuesta** en SB04, SB07, BC01, BC02, BC03, BC04,
  BC06, BC07 y RH02. En RH01 y RH05 las respuestas son equivalentes, aunque no idénticas. En BC03 y RH02
  el conjunto de fragmentos es el mismo; en BC03 incluso el orden.

### Casos con diferencias importantes

- **BC05** ("Wich dealer in Covent Gardn sold the geese to the Alpha Inn?"):
  - Con KMP, Watson respondió "The dealer in Covent Garden sold the geese to the Alpha Inn.", que no da el
    nombre. Con la búsqueda aproximada respondió "…was Breckinridge.".
  - **Observación:** los dos prompts tienen la **misma pregunta con errores** y el **mismo conjunto de
    cuatro fragmentos**; solo cambia el orden de los fragmentos 025 y 026.
  - **Interpretación:** la mejora no se puede atribuir a la corrección ortográfica, porque el modelo no
    recibe la pregunta corregida. Lo que se observa es que el modelo es sensible al orden del contexto.
- **SB06** ("What was the speckld band realy?"):
  - Con KMP, Watson respondió "a supernatural entity". Con la búsqueda aproximada, "a deadly snake" (parcial,
    porque además atribuye la muerte a Helen).
  - Los dos contextos incluyen el fragmento 049 ("It is a swamp adder!"). Con la búsqueda aproximada aparece
    primero y el resto del contexto cambia (001 en lugar de 023).
  - **Posible explicación:** la corrección cambió la puntuación de los fragmentos y, con ella, qué fragmentos
    entraron y en qué orden. No se puede separar el efecto de cada cosa.
- **SB02** ("Where did the ventilator in Helen Stoner's room lead?"):
  - Con la búsqueda aproximada, Watson respondió "The ventilator led to the bed." (incorrecta). Con KMP,
    "To the inside of the house" (parcial).
  - El contexto aproximado incluyó el fragmento 051 ("…this ventilator, and to the bell-rope which hung down
    to the bed") en lugar del 038.
  - **Posible explicación:** el modelo confundió el ventilador con el cordón de la campana, que aparecen en
    la misma frase.

### Cómo afectó el contexto a la respuesta de Qwen

- **Cuando el contexto no tenía la respuesta, Qwen casi nunca se abstuvo.** Inventó un dato en SB07 y BC07
  ("The curtains… were black.", "The carriage was black.") y en SB05 ("books and artifacts… manuscripts…
  paintings"). La única abstención apropiada fue RH06 con KMP y Z, y llegó después de citar frases
  irrelevantes.
- **Un fragmento relacionado pero equivocado lleva a respuestas equivocadas.** En SB03 el contexto tenía
  una linterna que ilumina la caja fuerte (fragmento 048), y Qwen la puso "on top of the iron safe".
- **El orden y la mezcla de fragmentos cambian la respuesta** aunque la evidencia esté presente (BC05,
  SB06, SB02).

### Casos donde había evidencia suficiente y Qwen respondió mal

Según la revisión preliminar:

| Pregunta | Motores | Respuesta | Evidencia en el contexto |
|---|---|---|---|
| BC03 | los tres | "Peterson's wife found the blue stone in the Countess of Morcar's jewel-case." | 012: "See what my wife found in its crop!" |
| SB06 | KMP, Z | "The speckled band was a supernatural entity…" | 049: "It is a swamp adder!" |
| BC05 | KMP, Z | Repite la pregunta sin dar el nombre | 024: "Breckinridge is his name" |
| SB02 | aproximada | "The ventilator led to the bed." | 035: "open a ventilator into another room" |
| SB01 | los tres (parcial) | Solo "Oh, my God!" | 016: "…It was the band! The speckled band!" |

Esto es coherente con el diagnóstico anterior de Watson: con Qwen2.5-0.5B, el principal límite está en la
generación. Aun con la evidencia en el contexto, el modelo la usa mal o no la usa.

## 4. Ventajas y limitaciones de los algoritmos clásicos de cadenas

**KMP y Z-function:**
- *Ventajas:* las coincidencias son exactas y verificables. KMP y Z produjeron exactamente las mismas
  coincidencias, puntuaciones y contextos. Combinados con el índice invertido, solo recorren los fragmentos
  candidatos: 23.5 de 49 en promedio con el filtro de relato. Además, son fáciles de explicar: cada
  resultado dice qué términos coincidieron y cuántas veces.
- *Limitaciones:* no toleran errores de escritura (RH04 y BC05 dependieron de palabras escritas mal) ni
  paráfrasis (RH03). En esta implementación en Python, recorrer cada fragmento carácter por carácter fue más
  lento que las operaciones de conjuntos de la búsqueda aproximada.

**Levenshtein + Jaccard:**
- *Ventajas:* recupera evidencia aunque la pregunta tenga errores (RH04) y puntúa todos los fragmentos sin
  depender de coincidencias literales.
- *Limitaciones:*
  - La corrección puede **cambiar palabras bien escritas** que no están en el vocabulario: `curtains` →
    `certain`, `stealing` → `staring`, `stored` → `storied`, `cooked` → `cocked`.
  - El costo de corregir crece con el vocabulario.
  - La similitud por n-gramas casi no descarta fragmentos (48.6 encontrados de 49 examinados).
  - Como la búsqueda exacta, no entiende sinónimos ni paráfrasis (RH03).

**En conjunto:** ninguna de las estrategias de búsqueda compensa los errores del modelo de lenguaje. En
estas pruebas, la diferencia entre motores en la calidad final es de una o dos respuestas, mientras que la
diferencia entre recibir la evidencia y responder bien sigue dependiendo sobre todo de Qwen.

## Pendiente de revisión humana

- Confirmar o corregir las 60 valoraciones de `reports/evaluation_review.json`, en especial los casos
  límite: SB01, SB02, RH02, RH05 y RH06.
- Llenar las columnas vacías de `data/evaluation_review.csv`.
- Decidir si la referencia corregida de RH05 debe reemplazar a la de `data/evaluation_questions.json`.
