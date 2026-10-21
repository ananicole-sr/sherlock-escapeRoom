# Revisión de la evaluación de Watson

> **Valoraciones preliminares hechas por IA, pendientes de revisión humana.** No son una evaluación humana. Se basan en `data/evaluation_results.json` (60 ejecuciones existentes; no se volvió a ejecutar nada) y en `data/evaluation_questions.json`.

## Criterios

- **Utilidad del contexto**: *suficiente* si el contexto que recibió Watson permite responder bien; *parcial* si permite solo una parte; *insuficiente* si no contiene la respuesta. En las preguntas sin respuesta, lo esperado es *insuficiente*.
- **Corrección** (según el relato y la respuesta esperada): *correcta*, *parcial*, *incorrecta* o *abstención* (apropiada o no apropiada según si el contexto permitía responder). Una respuesta que repite la pregunta sin dar el dato cuenta como incorrecta, no como abstención.
- **Respaldo en el contexto** (según el contexto que realmente recibió el modelo, no el relato completo): *completo* si todo lo que afirma está en el contexto; *parcial* si mezcla afirmaciones respaldadas con otras que no lo están; *sin respaldo* si lo principal no está en el contexto o lo contradice.
- No se clasificó por palabras clave, por `status=ok` ni por la sola presencia de una cita; cada respuesta se comparó con el texto de los fragmentos enviados.

## Resumen preliminar

| Motor | Utilidad del contexto | Corrección | Respaldo |
|---|---|---|---|
| KMP | suficiente: 13, insuficiente: 7 | incorrecta: 9, correcta: 7, parcial: 3, abstención: 1 | completo: 9, sin respaldo: 6, parcial: 5 |
| Z-function | suficiente: 13, insuficiente: 7 | incorrecta: 9, correcta: 7, parcial: 3, abstención: 1 | completo: 9, sin respaldo: 6, parcial: 5 |
| Búsqueda aproximada (Levenshtein + Jaccard) | suficiente: 14, insuficiente: 6 | correcta: 9, incorrecta: 7, parcial: 3, abstención: 1 | completo: 10, sin respaldo: 6, parcial: 4 |

Observaciones transversales:

- Z-function recibió exactamente el mismo contexto y produjo exactamente la misma respuesta que KMP en las 20 preguntas, por eso sus valoraciones coinciden.
- Con contexto suficiente, Watson respondió de forma incorrecta en SB06, BC03 y BC05 con KMP y Z, y en SB02 y BC03 con la búsqueda aproximada (BC03 falla con los tres motores). Además dio respuestas parciales en SB01, SB02 y RH02 con KMP y Z, y en SB01, SB06 y RH02 con la búsqueda aproximada.
- En las preguntas sin respuesta, solo se abstuvo en RH06; en SB07 y BC07 inventó un color con los tres motores.
- RH02: la comprobación automática marcó que la evidencia no llegó, pero el contexto incluía red_headed_league_045 con John Clay; el contexto sí era suficiente.
- La corrección de Levenshtein alteró palabras bien escritas en algunas preguntas (curtains → certain, stealing → staring, stored → storied, cooked → cocked); se registra sin cambiar nada.

## KMP

### SB01 · direct

**Pregunta:** What were the last words of Helen Stoner's sister?

**Respuesta esperada:** "It was the band! The speckled band!"

**Respuesta de Watson:** Helen Stoner's sister's final words were "Oh, my God!"

**Contexto recibido:** speckled_band_023, speckled_band_016, speckled_band_007, speckled_band_009

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: El contexto incluye speckled_band_016 con el grito completo: "Oh, my God! Helen! It was the band! The speckled band!". Watson cita solo "Oh, my God!" y lo presenta como sus palabras finales, omitiendo la parte esencial ("the speckled band").

### SB02 · direct

**Pregunta:** Where did the ventilator in Helen Stoner's room lead?

**Respuesta esperada:** Into another room (Dr. Roylott's), not to the outside air.

**Respuesta de Watson:** To the inside of the house

**Contexto recibido:** speckled_band_035, speckled_band_053, speckled_band_038, speckled_band_013

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: speckled_band_035 dice que el ventilador abre "into another room" y no al exterior; speckled_band_053 permite inferir que es el cuarto de Roylott (se subía a la silla para alcanzarlo). "To the inside of the house" no contradice el texto pero es vago: no dice que lleva a otro cuarto ni a cuál.

### SB03 · direct

**Pregunta:** What did Holmes find on top of the iron safe in Dr. Roylott's room?

**Respuesta esperada:** A small saucer of milk.

**Respuesta de Watson:** On top of the iron safe, Holmes found a dark lantern with a shutter half open, casting a bright beam of light onto the iron safe door.

**Contexto recibido:** speckled_band_048, speckled_band_040, speckled_band_002, speckled_band_030

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: El fragmento con el plato de leche (speckled_band_036) no llegó. speckled_band_048 dice que la linterna estaba "on the table" y alumbraba la caja fuerte; afirmar que estaba encima de la caja fuerte contradice el contexto.

### SB04 · paraphrase

**Pregunta:** Why could Helen Stoner not move her bed?

**Respuesta esperada:** It was clamped to the floor.

**Respuesta de Watson:** Helen Stoner could not move her bed because it was clamped to the floor.

**Contexto recibido:** speckled_band_042, speckled_band_032, speckled_band_033, speckled_band_051

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: speckled_band_042: "It was clamped to the floor" y "The lady could not move her bed".

### SB05 · misspelled

**Pregunta:** What animls did Dr. Roylot keep at Stoke Moran?
  
*Sin errores:* What animals did Dr. Roylott keep at Stoke Moran?

**Respuesta esperada:** A cheetah and a baboon (he had a passion for Indian animals).

**Respuesta de Watson:** Dr. Roylot kept a large collection of books and artifacts at Stoke Moran, including a collection of ancient manuscripts and a collection of rare paintings.

**Contexto recibido:** speckled_band_009, speckled_band_025, speckled_band_029, speckled_band_040

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Ningún fragmento del contexto menciona el guepardo, el babuino ni animales. Los libros, artefactos, manuscritos y pinturas no aparecen en el contexto: son inventados.

### SB06 · misspelled

**Pregunta:** What was the speckld band realy?
  
*Sin errores:* What was the speckled band really?

**Respuesta esperada:** A swamp adder, the deadliest snake in India.

**Respuesta de Watson:** The speckled band was a supernatural entity believed to be responsible for Helen's death.

**Contexto recibido:** speckled_band_018, speckled_band_049, speckled_band_016, speckled_band_023

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: speckled_band_049 está en el contexto: "It is a swamp adder! … the deadliest snake in India". "A supernatural entity" contradice el contexto, y quien murió fue la hermana de Helen, no Helen.

### SB07 · unanswerable

**Pregunta:** What colour were the curtains in Helen Stoner's bedroom?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The curtains in Helen Stoner's bedroom were black.

**Contexto recibido:** speckled_band_007, speckled_band_023, speckled_band_009, speckled_band_029

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Ni "curtain" ni "black" aparecen en el contexto. Debió abstenerse; inventa el color.

### BC01 · direct

**Pregunta:** Who picked up the hat and the goose after the fight on Tottenham Court Road?

**Respuesta esperada:** Peterson, the commissionaire.

**Respuesta de Watson:** Peterson picked up the hat and the goose after the fight on Tottenham Court Road.

**Contexto recibido:** blue_carbuncle_015, blue_carbuncle_004, blue_carbuncle_003, blue_carbuncle_005

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_004: Peterson quedó "in possession … of this battered hat and a most unimpeachable Christmas goose"; blue_carbuncle_003 lo identifica. Omite "commissionaire", detalle no esencial.

### BC02 · direct

**Pregunta:** What initials were written inside the hat?

**Respuesta esperada:** H. B. (the card on the goose read 'For Mrs. Henry Baker').

**Respuesta de Watson:** The initials "H. B." were written inside the hat.

**Contexto recibido:** blue_carbuncle_005, blue_carbuncle_006, blue_carbuncle_010, blue_carbuncle_008

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_006: "the initials 'H. B.' were scrawled upon one side" (también en 005).

### BC03 · direct

**Pregunta:** Where did Peterson's wife find the blue stone?

**Respuesta esperada:** In the crop of the goose.

**Respuesta de Watson:** Peterson's wife found the blue stone in the Countess of Morcar's jewel-case.

**Contexto recibido:** blue_carbuncle_012, blue_carbuncle_017, blue_carbuncle_014, blue_carbuncle_035

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: blue_carbuncle_012 está en el contexto: "See what my wife found in its crop!". Watson responde con el estuche de joyas de la condesa, que en blue_carbuncle_014 es de donde se robó la piedra, no donde la encontró la esposa de Peterson.

### BC04 · direct

**Pregunta:** Who was accused of stealing the Countess of Morcar's jewel?

**Respuesta esperada:** John Horner, a plumber.

**Respuesta de Watson:** John Horner was accused of stealing the Countess of Morcar's jewel.

**Contexto recibido:** blue_carbuncle_014, blue_carbuncle_013, blue_carbuncle_035, blue_carbuncle_012

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_014: "John Horner, 26, plumber, was brought up upon the charge …". Omite que era plomero, detalle no esencial.

### BC05 · misspelled

**Pregunta:** Wich dealer in Covent Gardn sold the geese to the Alpha Inn?
  
*Sin errores:* Which dealer in Covent Garden sold the geese to the Alpha Inn?

**Respuesta esperada:** Breckinridge.

**Respuesta de Watson:** The dealer in Covent Garden sold the geese to the Alpha Inn.

**Contexto recibido:** blue_carbuncle_024, blue_carbuncle_041, blue_carbuncle_026, blue_carbuncle_025

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_024 contiene "Breckinridge is his name". La respuesta repite la pregunta sin nombrar al vendedor: lo que afirma está en el contexto, pero no responde. No es una abstención.

### BC06 · misspelled

**Pregunta:** What was the real name of the man who called himself John Robinsn?
  
*Sin errores:* What was the real name of the man who called himself John Robinson?

**Respuesta esperada:** James Ryder.

**Respuesta de Watson:** The real name of the man who called himself John Robinson was James Ryder.

**Contexto recibido:** blue_carbuncle_032, blue_carbuncle_004, blue_carbuncle_025, blue_carbuncle_006

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_032: "is John Robinson" … "my real name is James Ryder".

### BC07 · unanswerable

**Pregunta:** What colour was the Countess of Morcar's carriage?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The Countess of Morcar's carriage was black.

**Contexto recibido:** blue_carbuncle_014, blue_carbuncle_012, blue_carbuncle_035, blue_carbuncle_013

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Ni "carriage" ni "black" aparecen en el contexto. Debió abstenerse; inventa el color.

### RH01 · direct

**Pregunta:** How much was Jabez Wilson paid each week by the Red-Headed League?

**Respuesta esperada:** Four pounds (£4) a week.

**Respuesta de Watson:** According to the passage, Jabez Wilson was paid £4 per week for being a member of the League.

**Contexto recibido:** red_headed_league_007, red_headed_league_001, red_headed_league_010, red_headed_league_011

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: red_headed_league_007: "a salary of £ 4 a week" para un miembro de la Liga.

### RH02 · direct

**Pregunta:** Who was caught in the bank cellar at the end of the case?

**Respuesta esperada:** John Clay.

**Respuesta de Watson:** At the end of the case, the assistant was caught in the bank cellar.

**Contexto recibido:** red_headed_league_048, red_headed_league_042, red_headed_league_045, red_headed_league_047

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: El fragmento de la cita guardada (044) no llegó, pero sí red_headed_league_045, donde John Clay es esposado ("said John Clay serenely"), y 047/048 vinculan al ayudante con el delincuente. Según el relato el ayudante es John Clay, así que la respuesta es correcta en lo esencial, pero no da el nombre que el contexto sí ofrecía. La comprobación automática marcó la evidencia como ausente; en realidad el contexto era suficiente.

### RH03 · paraphrase

**Pregunta:** Why was Jabez Wilson paid to copy the Encyclopaedia?

**Respuesta esperada:** To get him out of the way for a number of hours every day.

**Respuesta de Watson:** Jabez Wilson was paid to copy the _Encyclopædia Britannica_.

**Contexto recibido:** red_headed_league_019, red_headed_league_008, red_headed_league_003, red_headed_league_005

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **completo**
- Justificación: El fragmento con el motivo (red_headed_league_046) no llegó, y ningún otro del contexto lo explica. La respuesta solo repite que le pagaban por copiar la enciclopedia, sin dar el motivo; lo que afirma sí está en el contexto.

### RH04 · misspelled

**Pregunta:** Why did Holmes beat the pavment with his stik?
  
*Sin errores:* Why did Holmes beat the pavement with his stick?

**Respuesta esperada:** To find out whether the cellar stretched out in front or behind.

**Respuesta de Watson:** Holmes used his hunting crop to hit the man's wrist, causing him to fall down the hole.

**Contexto recibido:** red_headed_league_044, red_headed_league_024, red_headed_league_026, red_headed_league_001

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **parcial**
- Justificación: El fragmento con la explicación del pavimento (red_headed_league_048) no llegó. Watson describe otro momento: el golpe con el bastón de caza en la muñeca está en red_headed_league_044, pero "causing him to fall down the hole" no (es el otro hombre quien "dived down the hole"). No responde por qué golpeó el pavimento.

### RH05 · direct

**Pregunta:** What was stored in the crates in the bank cellar?

**Respuesta esperada:** French gold: napoleons, 2,000 in each crate, packed between layers of lead foil.

**Respuesta de Watson:** In the bank cellar, the crates contained 2,000 napoleons packed between layers of lead foil.

**Contexto recibido:** red_headed_league_045, red_headed_league_048, red_headed_league_038, red_headed_league_040

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: red_headed_league_040: "2,000 napoleons packed between layers of lead foil" y "Your French gold?". Omite "French gold" y es ambigua sobre si son 2,000 por caja o en total (el texto dice que esa caja contiene 2,000 de los 30,000).

### RH06 · unanswerable

**Pregunta:** What was the name of the girl who cooked for Jabez Wilson?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The passage mentions that "Jabez Wilson here has been good enough to call upon me this morning, and to begin a narrative which promises to be one of the most singular that I have ever listened to." The narrator states, "As a rule, when I have heard some slight indication of the course of events, I am able to guide myself by the thousands of other similar cases which occur to my memory." Therefore, the name of the girl who cooked for Jabez Wilson is not explicitly mentioned in the passage provided.

**Contexto recibido:** red_headed_league_005, red_headed_league_008, red_headed_league_003, red_headed_league_009

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **abstención (apropiada)**
- Respaldo en el contexto: **parcial**
- Justificación: Termina con "the name of the girl … is not explicitly mentioned", que es correcto: el contexto no la menciona. Pero antes cita dos frases irrelevantes, una alterada ("one of the most singular that I have ever listened to" frente a "one of the most singular which I have listened to for some time").

## Z-function

> El contexto y la respuesta son idénticos a KMP en las 20 ejecuciones (verificado carácter por carácter); las valoraciones repiten las de KMP.

### SB01 · direct

**Pregunta:** What were the last words of Helen Stoner's sister?

**Respuesta esperada:** "It was the band! The speckled band!"

**Respuesta de Watson:** Helen Stoner's sister's final words were "Oh, my God!"

**Contexto recibido:** speckled_band_023, speckled_band_016, speckled_band_007, speckled_band_009

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: El contexto incluye speckled_band_016 con el grito completo: "Oh, my God! Helen! It was the band! The speckled band!". Watson cita solo "Oh, my God!" y lo presenta como sus palabras finales, omitiendo la parte esencial ("the speckled band").

### SB02 · direct

**Pregunta:** Where did the ventilator in Helen Stoner's room lead?

**Respuesta esperada:** Into another room (Dr. Roylott's), not to the outside air.

**Respuesta de Watson:** To the inside of the house

**Contexto recibido:** speckled_band_035, speckled_band_053, speckled_band_038, speckled_band_013

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: speckled_band_035 dice que el ventilador abre "into another room" y no al exterior; speckled_band_053 permite inferir que es el cuarto de Roylott (se subía a la silla para alcanzarlo). "To the inside of the house" no contradice el texto pero es vago: no dice que lleva a otro cuarto ni a cuál.

### SB03 · direct

**Pregunta:** What did Holmes find on top of the iron safe in Dr. Roylott's room?

**Respuesta esperada:** A small saucer of milk.

**Respuesta de Watson:** On top of the iron safe, Holmes found a dark lantern with a shutter half open, casting a bright beam of light onto the iron safe door.

**Contexto recibido:** speckled_band_048, speckled_band_040, speckled_band_002, speckled_band_030

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: El fragmento con el plato de leche (speckled_band_036) no llegó. speckled_band_048 dice que la linterna estaba "on the table" y alumbraba la caja fuerte; afirmar que estaba encima de la caja fuerte contradice el contexto.

### SB04 · paraphrase

**Pregunta:** Why could Helen Stoner not move her bed?

**Respuesta esperada:** It was clamped to the floor.

**Respuesta de Watson:** Helen Stoner could not move her bed because it was clamped to the floor.

**Contexto recibido:** speckled_band_042, speckled_band_032, speckled_band_033, speckled_band_051

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: speckled_band_042: "It was clamped to the floor" y "The lady could not move her bed".

### SB05 · misspelled

**Pregunta:** What animls did Dr. Roylot keep at Stoke Moran?
  
*Sin errores:* What animals did Dr. Roylott keep at Stoke Moran?

**Respuesta esperada:** A cheetah and a baboon (he had a passion for Indian animals).

**Respuesta de Watson:** Dr. Roylot kept a large collection of books and artifacts at Stoke Moran, including a collection of ancient manuscripts and a collection of rare paintings.

**Contexto recibido:** speckled_band_009, speckled_band_025, speckled_band_029, speckled_band_040

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Ningún fragmento del contexto menciona el guepardo, el babuino ni animales. Los libros, artefactos, manuscritos y pinturas no aparecen en el contexto: son inventados.

### SB06 · misspelled

**Pregunta:** What was the speckld band realy?
  
*Sin errores:* What was the speckled band really?

**Respuesta esperada:** A swamp adder, the deadliest snake in India.

**Respuesta de Watson:** The speckled band was a supernatural entity believed to be responsible for Helen's death.

**Contexto recibido:** speckled_band_018, speckled_band_049, speckled_band_016, speckled_band_023

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: speckled_band_049 está en el contexto: "It is a swamp adder! … the deadliest snake in India". "A supernatural entity" contradice el contexto, y quien murió fue la hermana de Helen, no Helen.

### SB07 · unanswerable

**Pregunta:** What colour were the curtains in Helen Stoner's bedroom?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The curtains in Helen Stoner's bedroom were black.

**Contexto recibido:** speckled_band_007, speckled_band_023, speckled_band_009, speckled_band_029

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Ni "curtain" ni "black" aparecen en el contexto. Debió abstenerse; inventa el color.

### BC01 · direct

**Pregunta:** Who picked up the hat and the goose after the fight on Tottenham Court Road?

**Respuesta esperada:** Peterson, the commissionaire.

**Respuesta de Watson:** Peterson picked up the hat and the goose after the fight on Tottenham Court Road.

**Contexto recibido:** blue_carbuncle_015, blue_carbuncle_004, blue_carbuncle_003, blue_carbuncle_005

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_004: Peterson quedó "in possession … of this battered hat and a most unimpeachable Christmas goose"; blue_carbuncle_003 lo identifica. Omite "commissionaire", detalle no esencial.

### BC02 · direct

**Pregunta:** What initials were written inside the hat?

**Respuesta esperada:** H. B. (the card on the goose read 'For Mrs. Henry Baker').

**Respuesta de Watson:** The initials "H. B." were written inside the hat.

**Contexto recibido:** blue_carbuncle_005, blue_carbuncle_006, blue_carbuncle_010, blue_carbuncle_008

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_006: "the initials 'H. B.' were scrawled upon one side" (también en 005).

### BC03 · direct

**Pregunta:** Where did Peterson's wife find the blue stone?

**Respuesta esperada:** In the crop of the goose.

**Respuesta de Watson:** Peterson's wife found the blue stone in the Countess of Morcar's jewel-case.

**Contexto recibido:** blue_carbuncle_012, blue_carbuncle_017, blue_carbuncle_014, blue_carbuncle_035

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: blue_carbuncle_012 está en el contexto: "See what my wife found in its crop!". Watson responde con el estuche de joyas de la condesa, que en blue_carbuncle_014 es de donde se robó la piedra, no donde la encontró la esposa de Peterson.

### BC04 · direct

**Pregunta:** Who was accused of stealing the Countess of Morcar's jewel?

**Respuesta esperada:** John Horner, a plumber.

**Respuesta de Watson:** John Horner was accused of stealing the Countess of Morcar's jewel.

**Contexto recibido:** blue_carbuncle_014, blue_carbuncle_013, blue_carbuncle_035, blue_carbuncle_012

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_014: "John Horner, 26, plumber, was brought up upon the charge …". Omite que era plomero, detalle no esencial.

### BC05 · misspelled

**Pregunta:** Wich dealer in Covent Gardn sold the geese to the Alpha Inn?
  
*Sin errores:* Which dealer in Covent Garden sold the geese to the Alpha Inn?

**Respuesta esperada:** Breckinridge.

**Respuesta de Watson:** The dealer in Covent Garden sold the geese to the Alpha Inn.

**Contexto recibido:** blue_carbuncle_024, blue_carbuncle_041, blue_carbuncle_026, blue_carbuncle_025

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_024 contiene "Breckinridge is his name". La respuesta repite la pregunta sin nombrar al vendedor: lo que afirma está en el contexto, pero no responde. No es una abstención.

### BC06 · misspelled

**Pregunta:** What was the real name of the man who called himself John Robinsn?
  
*Sin errores:* What was the real name of the man who called himself John Robinson?

**Respuesta esperada:** James Ryder.

**Respuesta de Watson:** The real name of the man who called himself John Robinson was James Ryder.

**Contexto recibido:** blue_carbuncle_032, blue_carbuncle_004, blue_carbuncle_025, blue_carbuncle_006

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_032: "is John Robinson" … "my real name is James Ryder".

### BC07 · unanswerable

**Pregunta:** What colour was the Countess of Morcar's carriage?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The Countess of Morcar's carriage was black.

**Contexto recibido:** blue_carbuncle_014, blue_carbuncle_012, blue_carbuncle_035, blue_carbuncle_013

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Ni "carriage" ni "black" aparecen en el contexto. Debió abstenerse; inventa el color.

### RH01 · direct

**Pregunta:** How much was Jabez Wilson paid each week by the Red-Headed League?

**Respuesta esperada:** Four pounds (£4) a week.

**Respuesta de Watson:** According to the passage, Jabez Wilson was paid £4 per week for being a member of the League.

**Contexto recibido:** red_headed_league_007, red_headed_league_001, red_headed_league_010, red_headed_league_011

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: red_headed_league_007: "a salary of £ 4 a week" para un miembro de la Liga.

### RH02 · direct

**Pregunta:** Who was caught in the bank cellar at the end of the case?

**Respuesta esperada:** John Clay.

**Respuesta de Watson:** At the end of the case, the assistant was caught in the bank cellar.

**Contexto recibido:** red_headed_league_048, red_headed_league_042, red_headed_league_045, red_headed_league_047

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: El fragmento de la cita guardada (044) no llegó, pero sí red_headed_league_045, donde John Clay es esposado ("said John Clay serenely"), y 047/048 vinculan al ayudante con el delincuente. Según el relato el ayudante es John Clay, así que la respuesta es correcta en lo esencial, pero no da el nombre que el contexto sí ofrecía. La comprobación automática marcó la evidencia como ausente; en realidad el contexto era suficiente.

### RH03 · paraphrase

**Pregunta:** Why was Jabez Wilson paid to copy the Encyclopaedia?

**Respuesta esperada:** To get him out of the way for a number of hours every day.

**Respuesta de Watson:** Jabez Wilson was paid to copy the _Encyclopædia Britannica_.

**Contexto recibido:** red_headed_league_019, red_headed_league_008, red_headed_league_003, red_headed_league_005

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **completo**
- Justificación: El fragmento con el motivo (red_headed_league_046) no llegó, y ningún otro del contexto lo explica. La respuesta solo repite que le pagaban por copiar la enciclopedia, sin dar el motivo; lo que afirma sí está en el contexto.

### RH04 · misspelled

**Pregunta:** Why did Holmes beat the pavment with his stik?
  
*Sin errores:* Why did Holmes beat the pavement with his stick?

**Respuesta esperada:** To find out whether the cellar stretched out in front or behind.

**Respuesta de Watson:** Holmes used his hunting crop to hit the man's wrist, causing him to fall down the hole.

**Contexto recibido:** red_headed_league_044, red_headed_league_024, red_headed_league_026, red_headed_league_001

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **parcial**
- Justificación: El fragmento con la explicación del pavimento (red_headed_league_048) no llegó. Watson describe otro momento: el golpe con el bastón de caza en la muñeca está en red_headed_league_044, pero "causing him to fall down the hole" no (es el otro hombre quien "dived down the hole"). No responde por qué golpeó el pavimento.

### RH05 · direct

**Pregunta:** What was stored in the crates in the bank cellar?

**Respuesta esperada:** French gold: napoleons, 2,000 in each crate, packed between layers of lead foil.

**Respuesta de Watson:** In the bank cellar, the crates contained 2,000 napoleons packed between layers of lead foil.

**Contexto recibido:** red_headed_league_045, red_headed_league_048, red_headed_league_038, red_headed_league_040

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: red_headed_league_040: "2,000 napoleons packed between layers of lead foil" y "Your French gold?". Omite "French gold" y es ambigua sobre si son 2,000 por caja o en total (el texto dice que esa caja contiene 2,000 de los 30,000).

### RH06 · unanswerable

**Pregunta:** What was the name of the girl who cooked for Jabez Wilson?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The passage mentions that "Jabez Wilson here has been good enough to call upon me this morning, and to begin a narrative which promises to be one of the most singular that I have ever listened to." The narrator states, "As a rule, when I have heard some slight indication of the course of events, I am able to guide myself by the thousands of other similar cases which occur to my memory." Therefore, the name of the girl who cooked for Jabez Wilson is not explicitly mentioned in the passage provided.

**Contexto recibido:** red_headed_league_005, red_headed_league_008, red_headed_league_003, red_headed_league_009

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **abstención (apropiada)**
- Respaldo en el contexto: **parcial**
- Justificación: Termina con "the name of the girl … is not explicitly mentioned", que es correcto: el contexto no la menciona. Pero antes cita dos frases irrelevantes, una alterada ("one of the most singular that I have ever listened to" frente a "one of the most singular which I have listened to for some time").

## Búsqueda aproximada (Levenshtein + Jaccard)

### SB01 · direct

**Pregunta:** What were the last words of Helen Stoner's sister?

**Respuesta esperada:** "It was the band! The speckled band!"

**Respuesta de Watson:** Helen Stoner's sister whispered "Oh, my God!" after being struck by a metallic clang.

**Contexto recibido:** speckled_band_023, speckled_band_007, speckled_band_016, speckled_band_030

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: speckled_band_016 está en el contexto. "Oh, my God!" es parte del grito, pero falta lo esencial ("the speckled band"). "Whispered" contradice "shrieked"; el ruido metálico (speckled_band_023) lo oyó Helen y no se relaciona con esas palabras: es un detalle sin respaldo.

### SB02 · direct

**Pregunta:** Where did the ventilator in Helen Stoner's room lead?

**Respuesta esperada:** Into another room (Dr. Roylott's), not to the outside air.

**Respuesta de Watson:** The ventilator led to the bed.

**Contexto recibido:** speckled_band_053, speckled_band_035, speckled_band_051, speckled_band_013

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: speckled_band_035 dice "into another room". En speckled_band_051 lo que cuelga hasta la cama es el cordón de la campana; Watson los confunde.

### SB03 · direct

**Pregunta:** What did Holmes find on top of the iron safe in Dr. Roylott's room?

**Respuesta esperada:** A small saucer of milk.

**Respuesta de Watson:** Holmes found a dark lantern with a shutter half open on top of the iron safe in Dr. Roylott's room.

**Contexto recibido:** speckled_band_048, speckled_band_030, speckled_band_002, speckled_band_050

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: speckled_band_036 (el plato de leche) no llegó. En speckled_band_048 la linterna está "on the table" y no encima de la caja fuerte.

### SB04 · paraphrase

**Pregunta:** Why could Helen Stoner not move her bed?

**Respuesta esperada:** It was clamped to the floor.

**Respuesta de Watson:** Helen Stoner could not move her bed because it was clamped to the floor.

**Contexto recibido:** speckled_band_042, speckled_band_032, speckled_band_033, speckled_band_045

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: speckled_band_042: "It was clamped to the floor".

### SB05 · misspelled

**Pregunta:** What animls did Dr. Roylot keep at Stoke Moran?
  
*Sin errores:* What animals did Dr. Roylott keep at Stoke Moran?

**Respuesta esperada:** A cheetah and a baboon (he had a passion for Indian animals).

**Respuesta de Watson:** Dr. Roylot kept a small ventilation system in Stoke Moran, which he believed was unusual and potentially significant.

**Contexto recibido:** speckled_band_041, speckled_band_009, speckled_band_025, speckled_band_029

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Levenshtein corrigió bien la pregunta (animals, roylott), pero ningún fragmento con los animales llegó. El ventilador de speckled_band_041 está en el cuarto de Helen y no es algo que Roylott "tuviera"; "unusual and potentially significant" mezcla comentarios de Holmes.

### SB06 · misspelled

**Pregunta:** What was the speckld band realy?
  
*Sin errores:* What was the speckled band really?

**Respuesta esperada:** A swamp adder, the deadliest snake in India.

**Respuesta de Watson:** The speckled band was a deadly snake believed to be the cause of Helen's death.

**Contexto recibido:** speckled_band_049, speckled_band_018, speckled_band_016, speckled_band_001

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: speckled_band_049: "swamp adder … the deadliest snake in India". "A deadly snake" es correcto en lo esencial pero no la identifica como víbora de los pantanos. "The cause of Helen's death" no tiene respaldo: Helen no murió, murió su hermana.

### SB07 · unanswerable

**Pregunta:** What colour were the curtains in Helen Stoner's bedroom?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The curtains in Helen Stoner's bedroom were black.

**Contexto recibido:** speckled_band_009, speckled_band_007, speckled_band_023, speckled_band_013

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Inventa "black". Además, Levenshtein cambió "curtains" por "certain" en la búsqueda, aunque eso no habría permitido encontrar una respuesta que no existe.

### BC01 · direct

**Pregunta:** Who picked up the hat and the goose after the fight on Tottenham Court Road?

**Respuesta esperada:** Peterson, the commissionaire.

**Respuesta de Watson:** Peterson picked up the hat and the goose after the fight on Tottenham Court Road.

**Contexto recibido:** blue_carbuncle_004, blue_carbuncle_003, blue_carbuncle_015, blue_carbuncle_016

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_004 y 003, igual que con KMP.

### BC02 · direct

**Pregunta:** What initials were written inside the hat?

**Respuesta esperada:** H. B. (the card on the goose read 'For Mrs. Henry Baker').

**Respuesta de Watson:** The initials "H. B." were written inside the hat.

**Contexto recibido:** blue_carbuncle_010, blue_carbuncle_005, blue_carbuncle_006, blue_carbuncle_008

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_006 y 005: las iniciales "H. B.".

### BC03 · direct

**Pregunta:** Where did Peterson's wife find the blue stone?

**Respuesta esperada:** In the crop of the goose.

**Respuesta de Watson:** Peterson's wife found the blue stone in the Countess of Morcar's jewel-case.

**Contexto recibido:** blue_carbuncle_012, blue_carbuncle_017, blue_carbuncle_014, blue_carbuncle_035

- Utilidad del contexto: **suficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Mismo contexto que KMP, con blue_carbuncle_012 ("found in its crop"). Repite el error del estuche de joyas.

### BC04 · direct

**Pregunta:** Who was accused of stealing the Countess of Morcar's jewel?

**Respuesta esperada:** John Horner, a plumber.

**Respuesta de Watson:** John Horner was accused of stealing the Countess of Morcar's jewel.

**Contexto recibido:** blue_carbuncle_014, blue_carbuncle_035, blue_carbuncle_013, blue_carbuncle_012

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_014. Levenshtein cambió "stealing" por "staring", pero el fragmento correcto llegó igual.

### BC05 · misspelled

**Pregunta:** Wich dealer in Covent Gardn sold the geese to the Alpha Inn?
  
*Sin errores:* Which dealer in Covent Garden sold the geese to the Alpha Inn?

**Respuesta esperada:** Breckinridge.

**Respuesta de Watson:** The dealer in Covent Garden who sold the geese to the Alpha Inn was Breckinridge.

**Contexto recibido:** blue_carbuncle_024, blue_carbuncle_041, blue_carbuncle_025, blue_carbuncle_026

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_024: "I got the two dozen from a salesman in Covent Garden" … "Breckinridge is his name". Con el mismo fragmento disponible, aquí sí da el nombre.

### BC06 · misspelled

**Pregunta:** What was the real name of the man who called himself John Robinsn?
  
*Sin errores:* What was the real name of the man who called himself John Robinson?

**Respuesta esperada:** James Ryder.

**Respuesta de Watson:** The real name of the man who called himself John Robinson was James Ryder.

**Contexto recibido:** blue_carbuncle_032, blue_carbuncle_012, blue_carbuncle_016, blue_carbuncle_014

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: blue_carbuncle_032: alias John Robinson, nombre real James Ryder.

### BC07 · unanswerable

**Pregunta:** What colour was the Countess of Morcar's carriage?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The Countess of Morcar's carriage was black.

**Contexto recibido:** blue_carbuncle_035, blue_carbuncle_012, blue_carbuncle_014, blue_carbuncle_018

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **incorrecta**
- Respaldo en el contexto: **sin respaldo**
- Justificación: Inventa "black"; "carriage" no aparece en el contexto.

### RH01 · direct

**Pregunta:** How much was Jabez Wilson paid each week by the Red-Headed League?

**Respuesta esperada:** Four pounds (£4) a week.

**Respuesta de Watson:** Jabez Wilson was paid £4 a week by the Red-Headed League.

**Contexto recibido:** red_headed_league_007, red_headed_league_001, red_headed_league_029, red_headed_league_024

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: red_headed_league_007: "a salary of £ 4 a week".

### RH02 · direct

**Pregunta:** Who was caught in the bank cellar at the end of the case?

**Respuesta esperada:** John Clay.

**Respuesta de Watson:** At the end of the case, the assistant was caught in the bank cellar.

**Contexto recibido:** red_headed_league_042, red_headed_league_048, red_headed_league_045, red_headed_league_047

- Utilidad del contexto: **suficiente**
- Corrección: **parcial**
- Respaldo en el contexto: **parcial**
- Justificación: Mismos fragmentos que KMP (042, 048, 045, 047). red_headed_league_045 muestra a John Clay detenido; la respuesta habla del "assistant" (correcto según el relato) sin dar el nombre disponible.

### RH03 · paraphrase

**Pregunta:** Why was Jabez Wilson paid to copy the Encyclopaedia?

**Respuesta esperada:** To get him out of the way for a number of hours every day.

**Respuesta de Watson:** Jabez Wilson was paid to copy the Encyclopædia Britannica because he was part of the Red-Headed League, which was a secret society that operated under the guise of a charitable organization.

**Contexto recibido:** red_headed_league_019, red_headed_league_006, red_headed_league_049, red_headed_league_024

- Utilidad del contexto: **insuficiente**
- Corrección: **incorrecta**
- Respaldo en el contexto: **parcial**
- Justificación: red_headed_league_046 no llegó. Que pertenecía a la Liga sí está en el contexto. "A secret society that operated under the guise of a charitable organization" no aparece y es inventado.

### RH04 · misspelled

**Pregunta:** Why did Holmes beat the pavment with his stik?
  
*Sin errores:* Why did Holmes beat the pavement with his stick?

**Respuesta esperada:** To find out whether the cellar stretched out in front or behind.

**Respuesta de Watson:** Holmes beat the pavement with his stick because he wanted to ascertain whether the cellar stretched out in front or behind.

**Contexto recibido:** red_headed_league_029, red_headed_league_048, red_headed_league_030, red_headed_league_038

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: Levenshtein corrigió "pavment" y "stik", y llegó red_headed_league_048: "I was ascertaining whether the cellar stretched out in front or behind". La respuesta lo reproduce.

### RH05 · direct

**Pregunta:** What was stored in the crates in the bank cellar?

**Respuesta esperada:** French gold: napoleons, 2,000 in each crate, packed between layers of lead foil.

**Respuesta de Watson:** In the bank cellar, the crates contained 2,000 Napoleons packed between layers of lead foil.

**Contexto recibido:** red_headed_league_048, red_headed_league_040, red_headed_league_045, red_headed_league_038

- Utilidad del contexto: **suficiente**
- Corrección: **correcta**
- Respaldo en el contexto: **completo**
- Justificación: red_headed_league_040, igual que con KMP: napoleones en láminas de plomo. Omite "French gold" y es ambigua sobre la cantidad por caja. Levenshtein cambió "stored" por "storied" sin impedir la recuperación.

### RH06 · unanswerable

**Pregunta:** What was the name of the girl who cooked for Jabez Wilson?

**Respuesta esperada:** (sin respuesta en la colección)

**Respuesta de Watson:** The passage does not mention a girl named Cook for Jabez Wilson.

**Contexto recibido:** red_headed_league_005, red_headed_league_016, red_headed_league_024, red_headed_league_003

- Utilidad del contexto: **insuficiente (esperado: pregunta sin respuesta)**
- Corrección: **abstención (apropiada)**
- Respaldo en el contexto: **completo**
- Justificación: "The passage does not mention a girl …" es una abstención aunque no use la frase exacta, y es apropiada: "girl" no aparece en el contexto. Malinterpreta la pregunta como "a girl named Cook"; Levenshtein también cambió "cooked" por "cocked" en la búsqueda.

