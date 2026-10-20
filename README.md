# Sherlock Holmes — The Final Case

Escape room de investigación con recuperación de información (RAG sencillo):
algoritmos de strings para encontrar fragmentos de los relatos originales y un
modelo de Hugging Face para que Watson responda con ellos.

## Cómo correrlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentencepiece matplotlib

streamlit run app.py
```

Watson usa por defecto `Qwen/Qwen2.5-0.5B-Instruct` en CPU (~1 GB de descarga la
primera vez, ~2.3 GB de RAM cargado). Se empieza a cargar en segundo plano al
abrir la app. Para usar FLAN-T5 hay que elegirlo explícitamente:
`WATSON_MODEL=flan-t5 streamlit run app.py`. Solo se carga un modelo por proceso
y no hay respaldo automático: si el modelo elegido falla, Watson muestra el error.
Si algún día se usa un modelo privado, el token se lee de la variable `HF_TOKEN`
(nunca va en el código).

El vigilante de archivos está desactivado (`.streamlit/config.toml`), así que
después de editar el código hay que reiniciar `streamlit run app.py`.

## Organización

| Archivo | Qué hace |
|---|---|
| `app.py` | Entrada: tema, estado y navegación entre pantallas |
| `ui/state.py` | Estado del juego en `st.session_state` y validación de respuestas |
| `ui/investigation.py` | Expediente: escenario, Watson, cuaderno y deducción |
| `ui/lab.py` | Research Lab |
| `ui/screens.py` | Portada y conclusión |
| `ui/theme.py` | Estilos (paleta victoriana) |
| `ui/widgets.py` | Envoltorios de los componentes personalizados |
| `components/scene/` | Escenario con objetos clicables (HTML + JS, sin build) |
| `components/ask/` | Campo de preguntas con autocompletado del Trie |
| `data/cases.json` | Casos: textos, acertijos, respuestas y objetos con coordenadas |
| `static/scenes/` | Imágenes de los escenarios (servidas en `app/static/`) |
| `watson.py` | Selección de contexto, prompt y generación con Hugging Face |
| `trie.py`, `autocomplete.py` | Trie y sugerencias |
| `approximate_search.py`, `levenshtein.py`, `jaccard.py` | Búsqueda aproximada |
| `chunking.py`, `preprocess_chunks.py`, `inverted_index.py`, `text_cleaner.py` | Preparación de documentos e índice |

## Agregar o mover objetos en un escenario

Cada caso en `data/cases.json` tiene una lista `hotspots`. `x` y `y` son
porcentajes de la imagen (0–100), así que siguen alineados al cambiar el tamaño.
`note` es lo que se guarda en el cuaderno (`null` si no hay nada que guardar) y
`quote` es una cita literal del relato (`null` si es narrativa del juego).

Después de editar, verifica que las citas existan en los textos:

```bash
python test_case_content.py
```

## Búsqueda exacta (etapa 3)

El Research Lab muestra KMP y Z-function en cuanto exista `exact_search.py` con:

```python
search_exact(question, chunks, algorithm, top_k, story)   # algorithm: "kmp" o "z"
```

que devuelva el mismo formato que `search_approximate` (`query`, `algorithm`,
`retrieval_time_ms`, `chunks_examined`, `results` con `chunk_id`, `story`,
`text` y `score`).

## Pruebas

```bash
python test_trie.py
python test_case_content.py
python test_approximate_search.py
python test_watson_models.py qwen      # 4 preguntas de prueba, guarda data/watson_trial_qwen.json
python test_watson_models.py flan-t5   # lo mismo con FLAN-T5
```
