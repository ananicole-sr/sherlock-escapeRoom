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

```text
sherlock-escapeRoom/
├── app.py                 entrada de la aplicación (Streamlit)
├── requirements.txt
├── search/                etapas 1 a 4: documentos, índice y algoritmos
│   ├── chunking.py            divide los relatos en fragmentos
│   ├── text_cleaner.py        normalización y tokenización
│   ├── preprocess_chunks.py   texto normalizado y tokens de cada fragmento
│   ├── inverted_index.py      índice invertido y vocabulario
│   ├── query_processing.py    preprocesamiento común de las preguntas
│   ├── kmp.py · z_function.py · exact_search.py          búsqueda exacta
│   ├── levenshtein.py · jaccard.py · approximate_search.py   búsqueda aproximada
│   └── trie.py · autocomplete.py                          autocompletado
├── assistant/
│   └── watson.py          etapa 5: selección del contexto y modelo de lenguaje
├── ui/                    pantallas de la app y componentes (ui/components/)
├── static/                imágenes que sirve la app (escenarios, portada, Watson)
├── data/                  datos de producción: relatos, fragmentos, índice,
│                          vocabulario y casos del juego (cases.json)
├── evaluation/            etapa 6: scripts de evaluación, experimentos y gráficas
├── tests/                 pruebas
└── reports/               todo lo relacionado con reportes
    ├── reporte_etapas_5_6.md / .docx / .pdf    documento de las etapas 5 y 6
    ├── figures/           gráficas de la etapa 6 y sus números
    ├── results/           resultados de la evaluación y del experimento de tamaño
    ├── review/            evaluación asistida por IA (v1, v2 y correcciones)
    └── archive/           resultados intermedios (pruebas iniciales y diagnóstico de Watson)
```

## Agregar o mover objetos en un escenario

Cada caso en `data/cases.json` tiene una lista `hotspots`. `x` y `y` son
porcentajes de la imagen (0–100), así que siguen alineados al cambiar el tamaño.
`note` es lo que se guarda en el cuaderno (`null` si no hay nada que guardar) y
`quote` es una cita literal del relato (`null` si es narrativa del juego).

Después de editar, verifica que las citas existan en los textos:

```bash
python -m tests.test_case_content
```

## Comandos

Todos se corren desde la carpeta del proyecto (la que contiene `app.py`).

**Regenerar los datos de los documentos** (solo si cambian los relatos o la normalización):

```bash
python -m search.chunking            # data/chunks.json
python -m search.preprocess_chunks   # data/processed_chunks.json
python -m search.inverted_index      # data/inverted_index.json y data/vocabulary.json
```

**Pruebas:**

```bash
python -m tests.test_search_metrics      # KMP = Z, métricas de los buscadores
python -m tests.test_trie
python -m tests.test_case_content
python -m tests.test_approximate_search
```

**Evaluación de la etapa 6** (ya está hecha; los resultados están en `reports/`):

```bash
python -m evaluation.build_evaluation_questions   # verifica las 20 preguntas
python -m evaluation.run_evaluation               # 60 ejecuciones con Qwen (no sobrescribe resultados)
python -m evaluation.run_scaling_experiment       # colecciones de 1, 2 y 3 relatos
python -m evaluation.build_review_v2              # revisión asistida por IA, versión 2
python -m evaluation.make_stage6_figures          # reports/figures/
python -m evaluation.watson_trial qwen            # prueba rápida de Watson (4 preguntas)
python -m evaluation.diagnose_watson              # diagnóstico de Watson
```
