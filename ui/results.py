
# -------------------------------------------------------------------------
# Resultados y análisis: resultados de la etapa 6, leídos solo de archivos
# guardados. Abrir esta pantalla nunca ejecuta búsquedas, experimentos ni
# Qwen; si falta un archivo, se avisa junto con el script que lo genera.
# -------------------------------------------------------------------------

import html
import json
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
FIGURES = BASE_DIR / "reports" / "figures"

SOURCES = {
    "evaluation": (BASE_DIR / "reports" / "results" / "evaluation_results.json", "evaluation/run_evaluation.py"),
    "scaling": (BASE_DIR / "reports" / "results" / "scaling_results.json", "evaluation/run_scaling_experiment.py"),
    "review": (BASE_DIR / "reports" / "review" / "evaluation_review.json", "evaluation/build_review_v2.py"),
    "numbers": (FIGURES / "stage6_numbers.json", "evaluation/make_stage6_figures.py")
}

ENGINES = ["kmp", "z", "approximate"]
ENGINE_LABELS = {"kmp": "KMP", "z": "Z-function", "approximate": "Aproximada (Levenshtein + Jaccard)"}
ENGINE_IN_SENTENCE = {"kmp": "KMP", "z": "Z-function", "approximate": "la búsqueda aproximada"}

PRELIMINARY = ("Valoraciones preliminares hechas por IA, pendientes de revisión humana. No han sido "
               "validadas por una persona.")


def esc(text):
    return html.escape(str(text))


def shown(path):
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


@st.cache_data(show_spinner=False)
def read_json(path, modified):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load(name):
    path, script = SOURCES[name]

    if not path.exists():
        return None, (f"Falta <code>{esc(shown(path))}</code>. Lo genera "
                      f"<code>{esc(script)}</code>; esta pantalla no lo ejecuta.")

    try:
        return read_json(str(path), path.stat().st_mtime), None
    except (OSError, json.JSONDecodeError) as error:
        return None, f"No se pudo leer <code>{esc(shown(path))}</code>: {esc(error)}"


def missing(message):
    st.markdown(f"<div class='res-missing'><b>Resultado no disponible.</b> {message}</div>",
                unsafe_allow_html=True)


def figure(name, shows, observed, limits):
    path = FIGURES / name

    if path.exists():
        st.image(str(path), width="stretch")
    else:
        missing(f"Falta <code>reports/figures/{esc(name)}</code>. Lo genera "
                f"<code>evaluation/make_stage6_figures.py</code>.")

    st.markdown(
        "<div class='res-caption'>"
        f"<p><b>Qué muestra.</b> {shows}</p>"
        f"<p><b>Qué se observa.</b> {observed}</p>"
        f"<p><b>Limitaciones.</b> {limits}</p>"
        "</div>",
        unsafe_allow_html=True
    )


def table(rows, columns):
    head = "".join(f"<th>{esc(label)}</th>" for key, label in columns)
    body = ""

    for row in rows:
        body += "<tr>" + "".join(f"<td>{esc(row.get(key, ''))}</td>" for key, label in columns) + "</tr>"

    st.markdown(f"<div class='res-table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>",
                unsafe_allow_html=True)


# -------------------------------------------------------------------------
# 1. Eficiencia
# -------------------------------------------------------------------------

def draw_efficiency(numbers):
    evaluation = numbers["evaluation"]

    st.markdown(
        "<p class='res-lead'>60 ejecuciones guardadas: 20 preguntas × KMP, Z-function y búsqueda aproximada, "
        "con el filtro del relato de cada pregunta y top_k = 5. Búsqueda: 1 calentamiento y 5 repeticiones "
        "medidas por pregunta y motor. Generación: una respuesta nueva de Qwen2.5-0.5B-Instruct por "
        "ejecución, medida por separado.</p>",
        unsafe_allow_html=True
    )

    rows = []
    for engine in ENGINES:
        e = evaluation[engine]
        rows.append({
            "engine": ENGINE_LABELS[engine],
            "retrieval": f"{e['retrieval_mean_ms']:.1f} ms",
            "retrieval_median": f"{e['retrieval_median_ms']:.1f} ms",
            "generation": f"{e['generation_mean_ms'] / 1000:.2f} s",
            "candidates": e["candidates_mean"],
            "examined": e["examined_mean"],
            "matched": e["matched_mean"],
            "returned": e["returned_mean"],
            "evidence": f"{e['evidence_retrieved']}/{e['answerable']}"
        })

    table(rows, [("engine", "Motor"), ("retrieval", "Búsqueda (media)"), ("retrieval_median", "Búsqueda (mediana)"),
                 ("generation", "Generación (media, aparte)"), ("candidates", "Candidatos"),
                 ("examined", "Examinados"), ("matched", "Encontrados"), ("returned", "Devueltos"),
                 ("evidence", "Evidencia recuperada")])
    st.caption("Las cantidades de fragmentos son medias por pregunta. Candidatos: fragmentos que propone el "
               "índice invertido (búsqueda exacta) o toda la colección (aproximada). Examinados: fragmentos "
               "recorridos o puntuados después del filtro de relato. Encontrados: fragmentos con una "
               "coincidencia exacta (exacta) o con puntuación mayor que 0 (aproximada), antes de top_k. "
               "Devueltos: después de top_k.")

    fastest = min(ENGINES, key=lambda e: evaluation[e]["retrieval_mean_ms"])
    z_vs_kmp = evaluation["z"]["retrieval_mean_ms"] - evaluation["kmp"]["retrieval_mean_ms"]

    figure(
        "fig1_retrieval_time.png",
        "El tiempo de búsqueda de cada pregunta (media de 5 repeticiones), con la media (línea continua) y "
        "la mediana (línea punteada) de cada motor.",
        f"En estas ejecuciones, {ENGINE_IN_SENTENCE[fastest]} tuvo la media más baja "
        f"({evaluation[fastest]['retrieval_mean_ms']:.1f} ms). La búsqueda aproximada se divide en dos "
        "grupos: las preguntas en las que Levenshtein corrigió algún término tardaron 35–70 ms, y las demás "
        f"1–3 ms. Z-function tardó en promedio {z_vs_kmp:.1f} ms más que KMP, examinando exactamente los "
        "mismos fragmentos.",
        "Una sola máquina, una implementación en Python y 20 preguntas sobre 147 fragmentos. Esto no "
        "demuestra que un motor sea siempre más rápido: depende de los términos de la pregunta, del "
        "vocabulario y de la implementación."
    )

    figure(
        "fig2_generation_time.png",
        "El tiempo que tardó Qwen en escribir cada respuesta, medido aparte de la búsqueda.",
        "La generación tardó entre dos y tres órdenes de magnitud más que la búsqueda (unas 170 veces, en "
        "mediana), así que la elección del motor de búsqueda casi no cambia el tiempo total de respuesta. "
        "Las dos generaciones más lentas (RH06 con KMP y con Z) fueron respuestas largas.",
        "Hay una sola generación por pregunta y motor, en CPU; no se midió la variabilidad de la generación."
    )

    figure(
        "fig3_chunk_counts.png",
        "Cuántos fragmentos maneja cada motor por consulta, con el filtro de relato activado.",
        f"La búsqueda exacta parte de {evaluation['kmp']['candidates_mean']} candidatos del índice y recorre "
        f"{evaluation['kmp']['examined_mean']}; la aproximada puntúa los "
        f"{evaluation['approximate']['examined_mean']} fragmentos del relato, y los n-gramas de caracteres le "
        "dan una puntuación positiva a casi todos.",
        "\"Encontrados\" no significa lo mismo en los dos motores (coincidencia literal frente a puntuación "
        "mayor que 0), así que esas barras no se pueden comparar directamente."
    )


# -------------------------------------------------------------------------
# 2. Tamaño de la colección
# -------------------------------------------------------------------------

def draw_collection_size(numbers, scaling):
    st.markdown(
        "<p class='res-lead'>Subcolecciones reales de uno, dos y tres relatos, cada una con su propio índice "
        "invertido, vocabulario y n-gramas, preparados antes de medir. Sin filtro de relato. Cada orden de "
        "crecimiento usa las mismas preguntas, las de su relato base, así que el relato fuente está presente "
        "desde el primer tamaño. No se usó Qwen.</p>",
        unsafe_allow_html=True
    )

    rows = []
    for collection in scaling["collections"]:
        size = collection["size"]
        rows.append({
            "order": collection["order"],
            "stories": " + ".join(name.replace("The ", "") for name in size["story_names"]),
            "chunks": size["chunks"],
            "characters": f"{size['collection_characters']:,}",
            "terms": size["index_terms"],
            "prep": f"{collection['preparation_ms']['total_ms']:.1f} ms"
        })

    table(rows, [("order", "Orden"), ("stories", "Relatos"), ("chunks", "Fragmentos"), ("characters", "Caracteres"),
                 ("terms", "Términos del índice"), ("prep", "Preparación (fuera del tiempo de búsqueda)")])

    pivot = []
    for order in ["A", "B", "C"]:
        for engine in ENGINES:
            row = {"order": order, "engine": ENGINE_LABELS[engine]}
            for r in numbers["scaling"]:
                if r["order"] == order and r["engine"] == engine:
                    row[f"s{r['stories']}"] = f"{r['mean_ms']:.1f} ms ({r['chunks']} fragmentos)"
            pivot.append(row)

    table(pivot, [("order", "Orden"), ("engine", "Motor"), ("s1", "1 relato"), ("s2", "2 relatos"),
                  ("s3", "3 relatos")])
    st.caption("Tiempo medio de búsqueda sobre las preguntas de cada orden (5 repeticiones cada una, después "
               "de 1 calentamiento).")

    figure(
        "fig4_scaling_time.png",
        "El tiempo medio de búsqueda frente al número real de fragmentos, en los tres órdenes de crecimiento.",
        "En los órdenes B y C los tres motores tardan más a medida que crece la colección; en el orden A el "
        "tiempo baja de uno a dos relatos y vuelve a subir con tres. En estas mediciones, sin filtro de "
        "relato, la búsqueda aproximada tuvo la media más baja en todos los tamaños.",
        "Son solo tres tamaños y 6 o 7 preguntas por orden: la tendencia es orientativa, no una ley de "
        "crecimiento, y depende de qué palabras contiene cada relato."
    )

    figure(
        "fig5_scaling_examined.png",
        "Cuántos fragmentos examina cada motor a medida que crece la colección.",
        "La búsqueda aproximada examina toda la colección; la exacta, solo los candidatos del índice, que "
        "crecen más despacio. KMP y Z examinan exactamente los mismos fragmentos.",
        "Examinar menos fragmentos no hizo más rápida a la búsqueda exacta: cada fragmento examinado se "
        "recorre carácter por carácter en Python, una vez por cada término de la pregunta."
    )

    figure(
        "fig6_levenshtein_effect.png",
        "El tiempo de la búsqueda aproximada por pregunta y colección, separando las consultas que "
        "necesitaron corregir algún término.",
        "Las consultas que necesitaron corrección tardaron 14–73 ms, y las demás 2–17 ms. Con más relatos hay "
        "menos términos que corregir (por ejemplo, con un solo relato \"paid\" se cambió por \"pain\"), pero "
        "cada corrección recorre un vocabulario más grande, así que la media de este motor mezcla dos efectos "
        "opuestos.",
        "En este experimento no se midió por separado el tiempo de la corrección; es una observación sobre "
        "estas consultas."
    )


# -------------------------------------------------------------------------
# 3. Contexto y respuestas
# -------------------------------------------------------------------------

EXAMPLES = [
    ("similar", "BC03",
     "Los tres motores enviaron los mismos cuatro fragmentos, en el mismo orden, y Watson dio la misma "
     "respuesta equivocada. La evidencia (\"See what my wife found in its crop!\") estaba en el contexto: es "
     "un fallo de generación, no de búsqueda."),
    ("similar", "SB04",
     "Todos los motores recuperaron el pasaje \"It was clamped to the floor\" y dieron la misma respuesta "
     "correcta."),
    ("different", "BC05",
     "KMP y la búsqueda aproximada enviaron la misma pregunta con errores y los mismos cuatro fragmentos; solo "
     "cambió el orden de dos fragmentos. La mejora no se puede atribuir a la corrección ortográfica, porque el "
     "modelo nunca recibe la pregunta corregida: muestra que la respuesta depende del orden del contexto."),
    ("different", "RH04",
     "Levenshtein corrigió \"pavment\" y \"stik\", y la búsqueda aproximada recuperó la explicación de Holmes "
     "(fragmento 048). La búsqueda exacta buscó las palabras tal como estaban escritas y la evidencia no llegó "
     "al modelo."),
    ("different", "SB02",
     "El contexto de la búsqueda aproximada incluyó el fragmento 051, donde el ventilador y el cordón de la "
     "campana \"which hung down to the bed\" aparecen en la misma frase, y la respuesta los confundió. La "
     "respuesta con KMP es vaga, pero no es incorrecta.")
]


def draw_context_answers(numbers, evaluation, review):
    st.markdown(f"<div class='res-preliminary'><b>Preliminar.</b> {PRELIMINARY}</div>", unsafe_allow_html=True)

    quality = numbers["quality_preliminary_ai"]
    rows = []
    for engine in ENGINES:
        q = quality[engine]
        rows.append({
            "engine": ENGINE_LABELS[engine],
            "useful": f"{q['context_usefulness']['sufficient']}/20",
            "correct": q["correctness"]["correct"],
            "partial": q["correctness"]["partial"],
            "incorrect": q["correctness"]["incorrect"],
            "abstained": f"{q['correctness']['appropriate abstention']} / {q['correctness']['invalid abstention']}",
            "supported": q["support"]["complete"],
            "unsupported": q["support"]["unsupported"]
        })

    table(rows, [("engine", "Motor"), ("useful", "Contexto suficiente"), ("correct", "Correctas"),
                 ("partial", "Parciales"), ("incorrect", "Incorrectas"),
                 ("abstained", "Abstenciones (apropiadas / no válidas)"),
                 ("supported", "Respaldo completo"), ("unsupported", "Sin respaldo")])

    figure(
        "fig7_quality_preliminary.png",
        "Para cada ejecución: si el contexto permitía responder, si la respuesta es correcta según el relato "
        "y si lo que afirma está respaldado por el contexto que el modelo recibió realmente.",
        "La búsqueda aproximada tuvo dos respuestas correctas más que KMP y Z (8 contra 6) y una ejecución "
        "más con contexto suficiente. Con los tres motores, Qwen inventó respuestas para preguntas que no "
        "tienen respuesta en los documentos (SB07, BC07), y en varias ejecuciones respondió mal aun con la "
        "evidencia en el contexto.",
        "Son 20 preguntas y un solo revisor, que es una IA. Una diferencia de una o dos respuestas no basta "
        "para afirmar que una estrategia es mejor en general."
    )

    entries = {(e["id"], e["engine"]): e for e in review["entries"]}
    runs = {(r["id"], r["algorithm"]): r for r in evaluation["results"]}
    identical = sum(1 for (qid, engine) in runs if engine == "kmp"
                    and runs[(qid, "kmp")]["answer"] == runs[(qid, "z")]["answer"]
                    and [c["excerpt"] for c in runs[(qid, "kmp")]["context"]]
                    == [c["excerpt"] for c in runs[(qid, "z")]["context"]])

    st.markdown(
        f"<p class='res-lead'><b>KMP y Z-function</b> enviaron exactamente el mismo contexto y obtuvieron "
        f"exactamente la misma respuesta en {identical} de las 20 preguntas: los dos algoritmos encuentran las "
        "mismas coincidencias; solo cambia el tiempo.</p>",
        unsafe_allow_html=True
    )

    st.caption("Las preguntas y las respuestas de Watson se muestran tal como se registraron, en inglés.")

    for kind, title in [("similar", "Resultados similares"), ("different", "Diferencias importantes")]:
        st.markdown(f"<h3 class='res-h3'>{title}</h3>", unsafe_allow_html=True)

        for example_kind, qid, explanation in EXAMPLES:
            if example_kind != kind:
                continue

            question = runs[(qid, "kmp")]["question"]
            cards = ""

            for engine in ["kmp", "approximate"]:
                run = runs[(qid, engine)]
                entry = entries.get((qid, engine), {})
                context = ", ".join(c["chunk_id"].split("_")[-1] for c in run["context"])
                cards += (
                    f"<div class='res-answer'><div class='res-engine'>{esc(ENGINE_LABELS[engine])}</div>"
                    f"<div class='res-text'>{esc(run['answer'])}</div>"
                    f"<div class='res-meta'>fragmentos del contexto: {esc(context)} · valoración preliminar de "
                    f"IA: {esc(entry.get('correctness', '—'))} / respaldo {esc(entry.get('support', '—'))}"
                    f"</div></div>"
                )

            st.markdown(
                f"<div class='res-example'><div class='res-q'><span>{esc(qid)}</span> {esc(question)}</div>"
                f"<div class='res-answers'>{cards}</div><p class='res-why'>{esc(explanation)}</p></div>",
                unsafe_allow_html=True
            )


def draw_results():
    st.markdown(
        "<div class='lab-head'><h1>Resultados y análisis</h1>"
        "<p>Etapa 6: cómo se comparan las tres estrategias de búsqueda, cómo cambia el tiempo de búsqueda con "
        "el tamaño de la colección y cómo influyó el contexto recuperado en las respuestas de Watson. Todo lo "
        "que aparece aquí se lee de resultados guardados; al abrir esta pantalla no se ejecuta nada.</p></div>",
        unsafe_allow_html=True
    )

    numbers, numbers_error = load("numbers")
    evaluation, evaluation_error = load("evaluation")
    scaling, scaling_error = load("scaling")
    review, review_error = load("review")

    efficiency, size, quality = st.tabs(["Eficiencia", "Tamaño de la colección", "Contexto y respuestas"])

    with efficiency:
        if numbers_error:
            missing(numbers_error)
        else:
            draw_efficiency(numbers)

    with size:
        if numbers_error or scaling_error:
            missing(numbers_error or scaling_error)
        else:
            draw_collection_size(numbers, scaling)

    with quality:
        problem = numbers_error or evaluation_error or review_error
        if problem:
            missing(problem)
        else:
            draw_context_answers(numbers, evaluation, review)
