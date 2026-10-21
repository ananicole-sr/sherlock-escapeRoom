# Correcciones a la revisión de la evaluación (versión 2)

> **Valoraciones preliminares hechas por IA, pendientes de revisión humana.**
> La versión 1 (`reports/evaluation_review.md`) se conserva sin cambios. La versión 2
> (`reports/evaluation_review.json`, generada con `build_review_v2.py`) aplica las correcciones
> de este documento. Las respuestas reales y los contextos registrados en
> `data/evaluation_results.json` no se modificaron, y tampoco `data/evaluation_questions.json`.

## 1. SB02 con KMP y Z-function: respuesta incompleta, no sin respaldo

- **Respuesta registrada:** "To the inside of the house"
- **Fuente:** `speckled_band_035`: "what a fool a builder must be to open a ventilator into another room,
  when, with the same trouble, he might have communicated with the outside air!"
- **Versión 1:** corrección *parcial*, respaldo *parcial*.
- **Versión 2:** corrección *parcial*, respaldo **completo**.
- **Motivo:** que el ventilador da al interior de la casa se deduce de "into another room" en lugar de
  "the outside air". La respuesta es incompleta, porque no dice que lleva a otro cuarto ni que es el de
  Roylott, pero no hace ninguna afirmación sin respaldo. La versión 1 mezclaba lo incompleto con la falta de
  respaldo.

## 2. RH05: la referencia "2,000 en cada caja" no está en el texto

- **Fuente:** `red_headed_league_040`:
  - "borrowed for that purpose 30,000 napoleons from the Bank of France"
  - "The crate upon which I sit contains 2,000 napoleons packed between layers of lead foil."
- El relato da la cantidad de **una** caja y el total prestado. "crates" aparece una sola vez
  ("piled all round with crates and massive boxes") y no hay ninguna frase que diga "each crate".
- **Referencia en la versión 1:** "French gold: napoleons, 2,000 in each crate, packed between layers of
  lead foil."
- **Referencia en la versión 2:** "French gold: napoleons packed between layers of lead foil. The crate
  Merryweather sits on contains 2,000 napoleons; 30,000 were borrowed in total."
- **Respuestas registradas:** "In the bank cellar, the crates contained 2,000 napoleons packed between
  layers of lead foil." (KMP y Z), y la misma con "Napoleons" en la búsqueda aproximada.
- **Versión 1:** corrección *correcta*, respaldo *completo*, en los tres motores.
- **Versión 2:** corrección **parcial**, respaldo **parcial**, en los tres motores.
- **Motivo:** la respuesta identifica bien el contenido (napoleones entre láminas de plomo), pero atribuye a
  "the crates" la cantidad de una sola caja, lo que contradice el total de 30,000, y omite que es oro
  francés. La versión 1 la aceptó porque la referencia tenía la misma generalización.
- `data/evaluation_questions.json` conserva la referencia original, porque es la que se usó en las 60
  ejecuciones. La referencia corregida está en `reports/evaluation_review.json` (`corrected_references`).

## 3. RH06 con búsqueda aproximada: no es una abstención válida

- **Pregunta:** "What was the name of the girl who cooked for Jabez Wilson?"
- **Respuesta registrada:** "The passage does not mention a girl named Cook for Jabez Wilson."
- **Versión 1:** *abstención (apropiada)*, respaldo *completo*.
- **Versión 2:** **abstención (no válida)**, respaldo *completo*.
- **Motivo:** lo que afirma es cierto para el contexto que recibió (ningún fragmento menciona a una chica) y
  no inventa nada. Pero toma "cooked" como el nombre "Cook" y niega algo que la pregunta no plantea: no dice
  que el nombre de la chica no esté disponible. Abstenerse habría sido apropiado, pero esta respuesta no es
  una abstención sobre la pregunta que se hizo.
- **Nota:** en la búsqueda, Levenshtein corrigió "cooked" por "cocked", porque "cooked" no está en el
  vocabulario. No hay forma de saber si eso influyó en la lectura del modelo, que recibe la pregunta original.

## Efecto en los conteos (versión 2)

| Motor | Correcta | Parcial | Incorrecta | Abstención apropiada | Abstención no válida |
|---|---|---|---|---|---|
| KMP | 6 | 4 | 9 | 1 | 0 |
| Z-function | 6 | 4 | 9 | 1 | 0 |
| Búsqueda aproximada | 8 | 4 | 7 | 0 | 1 |
