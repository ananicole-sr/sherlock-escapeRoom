
# -------------------------------------------------------------------------
# Stage 6 figures, made only from saved results (nothing is re-run):
#   reports/results/evaluation_results.json   60 runs (20 questions x KMP, Z, approximate)
#   reports/results/scaling_results.json      retrieval time vs collection size
#   reports/review/evaluation_review.json preliminary AI review (version 2)
#
# Output: reports/figures/*.png and reports/figures/stage6_numbers.json
# (the numbers behind the figures, reused by the app and the analysis).
# -------------------------------------------------------------------------

import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
EVALUATION = BASE_DIR / "reports" / "results" / "evaluation_results.json"
SCALING = BASE_DIR / "reports" / "results" / "scaling_results.json"
REVIEW = BASE_DIR / "reports" / "review" / "evaluation_review.json"
FIGURES = BASE_DIR / "reports" / "figures"

ENGINES = ["kmp", "z", "approximate"]
ENGINE_LABELS = {"kmp": "KMP", "z": "Z-function", "approximate": "Aproximada"}

# Categorical slots 1-3 of the validated reference palette (all-pairs pass on
# the paper surface; aqua is below 3:1, so every series is directly labeled).
ENGINE_COLORS = {"kmp": "#2a78d6", "z": "#eb6834", "approximate": "#1baf7a"}

SURFACE = "#fbf8f1"
INK = "#2a1f15"
INK_2 = "#5b4733"
GRID = "#e6dfd0"

# Ordinal ramp (validated): best -> worst, plus neutral grays for abstentions.
ORDINAL = ["#0d3a73", "#2a68b8", "#6ea4e6"]
NEUTRAL = "#9a958a"

ORDERS = {"A": "base: The Speckled Band", "B": "base: The Blue Carbuncle", "C": "base: The Red-Headed League"}

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
    "legend.frameon": False,
    "legend.fontsize": 9,
    "savefig.dpi": 160,
    "savefig.facecolor": SURFACE,
    "savefig.bbox": "tight"
})


def load(path):
    if not path.exists():
        raise SystemExit(f"Falta el archivo de entrada: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save(figure, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURES / name)
    plt.close(figure)
    print("saved", FIGURES / name)


def note(figure, text):
    figure.text(0.0, -0.02, text, ha="left", va="top", fontsize=8.5, color=INK_2, wrap=True)


# -------------------------------------------------------------------------
# Evaluation runs (60)
# -------------------------------------------------------------------------

def evaluation_numbers(runs):
    numbers = {}

    for engine in ENGINES:
        rows = [r for r in runs if r["algorithm"] == engine]
        retrieval = [r["retrieval_timing"]["engine_reported_mean_ms"] for r in rows]
        generation = [r["generation_time_ms"] for r in rows]

        numbers[engine] = {
            "runs": len(rows),
            "retrieval_mean_ms": round(statistics.mean(retrieval), 2),
            "retrieval_median_ms": round(statistics.median(retrieval), 2),
            "retrieval_min_ms": round(min(retrieval), 2),
            "retrieval_max_ms": round(max(retrieval), 2),
            "generation_mean_ms": round(statistics.mean(generation), 1),
            "generation_median_ms": round(statistics.median(generation), 1),
            "generation_min_ms": round(min(generation), 1),
            "generation_max_ms": round(max(generation), 1),
            "candidates_mean": round(statistics.mean(r["metrics"]["candidates_considered"] for r in rows), 1),
            "examined_mean": round(statistics.mean(r["metrics"]["chunks_examined"] for r in rows), 1),
            "matched_mean": round(statistics.mean(r["metrics"]["chunks_matched"] for r in rows), 1),
            "returned_mean": round(statistics.mean(r["metrics"]["results_returned"] for r in rows), 1),
            "evidence_retrieved": sum(1 for r in rows if r["type"] != "unanswerable" and r["evidence_retrieved"]),
            "answerable": sum(1 for r in rows if r["type"] != "unanswerable")
        }

    return numbers


def strip_chart(runs, values, title, ylabel, name, explanation, unit_format):
    figure, axis = plt.subplots(figsize=(7.2, 3.8))
    labels = []

    for position, engine in enumerate(ENGINES):
        rows = [r for r in runs if r["algorithm"] == engine]
        ys = [values(r) for r in rows]
        xs = [position + (i % 5 - 2) * 0.05 for i in range(len(ys))]

        axis.scatter(xs, ys, s=34, color=ENGINE_COLORS[engine], edgecolor=SURFACE, linewidth=1.5,
                     zorder=3, label=ENGINE_LABELS[engine])

        mean = statistics.mean(ys)
        median = statistics.median(ys)
        axis.hlines(mean, position - 0.28, position + 0.28, color=INK, linewidth=2, zorder=4)
        axis.hlines(median, position - 0.28, position + 0.28, color=INK, linewidth=1.2,
                    linestyles=(0, (1, 2)), zorder=4)
        labels.append((position, mean, median))

    axis.set_xticks(range(len(ENGINES)), [ENGINE_LABELS[e] for e in ENGINES])
    axis.set_xlim(-0.5, len(ENGINES) - 0.1)
    axis.set_ylim(bottom=0)

    # Labels of a close mean and median are pushed apart instead of overlapping.
    gap = axis.get_ylim()[1] * 0.05
    for position, mean, median in labels:
        mean_y, median_y = mean, median
        if abs(mean - median) < gap:
            mean_y = max(mean, median) + gap / 2
            median_y = min(mean, median) - gap / 2
        axis.text(position + 0.32, mean_y, f"media {unit_format(mean)}", va="center", fontsize=8.5, color=INK)
        axis.text(position + 0.32, median_y, f"mediana {unit_format(median)}", va="center", fontsize=8.5,
                  color=INK_2)

    axis.set_ylabel(ylabel)
    axis.set_title(title, loc="left")
    axis.grid(axis="x", visible=False)
    note(figure, explanation)
    save(figure, name)


def chunk_counts_chart(numbers):
    measures = [("candidates_mean", "Candidatos"), ("examined_mean", "Fragmentos\nexaminados"),
                ("matched_mean", "Fragmentos encontrados\n(antes de top_k)"), ("returned_mean", "Resultados\ndevueltos")]
    figure, axis = plt.subplots(figsize=(7.6, 3.9))
    width = 0.24

    for offset, engine in enumerate(ENGINES):
        xs = [i + (offset - 1) * (width + 0.02) for i in range(len(measures))]
        ys = [numbers[engine][key] for key, label in measures]
        axis.bar(xs, ys, width=width, color=ENGINE_COLORS[engine], label=ENGINE_LABELS[engine],
                 edgecolor=SURFACE, linewidth=1)
        for x, y in zip(xs, ys):
            axis.text(x, y + 0.6, f"{y:.1f}", ha="center", va="bottom", fontsize=7.5, color=INK)

    axis.set_xticks(range(len(measures)), [label for key, label in measures])
    axis.set_ylabel("Media por pregunta (fragmentos)")
    axis.set_title("Fragmentos por consulta (con filtro de relato, top_k = 5)", loc="left")
    axis.legend(ncol=3, loc="upper right")
    axis.grid(axis="x", visible=False)
    note(figure, "Medias sobre las 20 preguntas de las 60 ejecuciones guardadas. La búsqueda exacta toma los "
                 "candidatos del índice invertido y solo recorre los del relato de la pregunta; la aproximada "
                 "no usa índice y puntúa todos los fragmentos del relato. Los n-gramas de caracteres le dan una "
                 "puntuación pequeña a casi cualquier fragmento, así que sus 'encontrados' casi igualan a sus "
                 "'examinados'.")
    save(figure, "fig3_chunk_counts.png")


# -------------------------------------------------------------------------
# Collection size experiment
# -------------------------------------------------------------------------

def scaling_numbers(scaling):
    rows = []

    for order in ORDERS:
        for stories in (1, 2, 3):
            for engine in ENGINES:
                runs = [r for r in scaling["runs"] if r["order"] == order and r["stories"] == stories
                        and r["engine"] == engine]
                times = [r["timing"]["engine_reported_mean_ms"] for r in runs]
                answerable = [r for r in runs if r["answerable"]]
                rows.append({
                    "order": order,
                    "stories": stories,
                    "chunks": runs[0]["chunks"],
                    "characters": runs[0]["collection_characters"],
                    "engine": engine,
                    "questions": len(runs),
                    "mean_ms": round(statistics.mean(times), 2),
                    "median_ms": round(statistics.median(times), 2),
                    "examined_mean": round(statistics.mean(r["chunks_examined"] for r in runs), 1),
                    "matched_mean": round(statistics.mean(r["chunks_matched"] for r in runs), 1),
                    "returned_mean": round(statistics.mean(r["results_returned"] for r in runs), 1),
                    "evidence_in_top_k": sum(1 for r in answerable if r["evidence_rank_in_top_k"] is not None),
                    "answerable": len(answerable)
                })

    return rows


def scaling_chart(rows, key, ylabel, title, name, explanation, exact_identical=False):
    figure, axes = plt.subplots(1, 3, figsize=(10.5, 3.6), sharey=True)

    for axis, (order, label) in zip(axes, ORDERS.items()):
        for engine in ["z", "kmp", "approximate"]:
            points = sorted((r["chunks"], r[key]) for r in rows if r["order"] == order and r["engine"] == engine)
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            dashed = exact_identical and engine == "kmp"
            axis.plot(xs, ys, color=ENGINE_COLORS[engine], linewidth=2, marker="o", markersize=6,
                      markeredgecolor=SURFACE, markeredgewidth=1.5, label=ENGINE_LABELS[engine],
                      linestyle=(0, (3, 2)) if dashed else "-")
            if exact_identical and engine == "z":
                continue
            text = "KMP = Z-function" if dashed else ENGINE_LABELS[engine]
            axis.annotate(text, (xs[-1], ys[-1]), xytext=(6, 0),
                          textcoords="offset points", va="center", fontsize=8, color=INK)

        axis.set_title(f"Orden {order} · {label}", loc="left", fontsize=10)
        axis.set_xlabel("Tamaño de la colección (fragmentos)")
        axis.set_xlim(right=max(r["chunks"] for r in rows) * 1.28)
        axis.set_ylim(bottom=0)

    axes[0].set_ylabel(ylabel)
    figure.suptitle(title, x=0.0, ha="left", fontsize=12, fontweight="bold", color=INK, y=1.04)
    note(figure, explanation)
    save(figure, name)


def levenshtein_chart(scaling):
    figure, axis = plt.subplots(figsize=(7.2, 3.8))
    runs = [r for r in scaling["runs"] if r["engine"] == "approximate"]

    for corrected, label, face in [(True, "La consulta necesitó corrección", ENGINE_COLORS["approximate"]),
                                   (False, "Sin corrección", SURFACE)]:
        selected = [r for r in runs
                    if (sum(a != b for a, b in zip(r["query_terms"], r["corrected_terms"])) > 0) == corrected]
        axis.scatter([r["chunks"] for r in selected], [r["timing"]["engine_reported_mean_ms"] for r in selected],
                     s=40, facecolor=face, edgecolor=ENGINE_COLORS["approximate"], linewidth=1.6,
                     label=f"{label} (n={len(selected)})", zorder=3)

    axis.set_xlabel("Tamaño de la colección (fragmentos)")
    axis.set_ylabel("Tiempo de búsqueda (ms, media de 5)")
    axis.set_title("Búsqueda aproximada: las consultas con corrección ortográfica tardaron más", loc="left")
    axis.set_ylim(bottom=0)
    axis.legend(loc="upper left")
    note(figure, "Cada punto es una pregunta en una subcolección (de los tres órdenes de crecimiento). Si un "
                 "término de la pregunta no está en el vocabulario, Levenshtein lo compara con todo el "
                 "vocabulario, que crece con la colección. Con más relatos hay menos términos que corregir, así "
                 "que la media de este motor mezcla dos efectos opuestos.")
    save(figure, "fig6_levenshtein_effect.png")


# -------------------------------------------------------------------------
# Preliminary AI review
# -------------------------------------------------------------------------

QUALITY = [
    ("context_usefulness", "Utilidad del contexto",
     [("suficiente", "sufficient", ORDINAL[0], None), ("parcial", "partial", ORDINAL[1], None),
      ("insuficiente", "insufficient", ORDINAL[2], None)]),
    ("correctness", "Corrección de la respuesta",
     [("correcta", "correct", ORDINAL[0], None), ("parcial", "partial", ORDINAL[1], None),
      ("incorrecta", "incorrect", ORDINAL[2], None),
      ("abstención (apropiada)", "appropriate abstention", NEUTRAL, None),
      ("abstención (no válida)", "invalid abstention", NEUTRAL, "////")]),
    ("support", "Respaldo en el contexto",
     [("completo", "complete", ORDINAL[0], None), ("parcial", "partial", ORDINAL[1], None),
      ("sin respaldo", "unsupported", ORDINAL[2], None)])
]


LEGEND_LABELS = {
    "sufficient": "suficiente", "partial": "parcial", "insufficient": "insuficiente",
    "correct": "correcta", "incorrect": "incorrecta",
    "appropriate abstention": "abstención apropiada", "invalid abstention": "abstención no válida",
    "complete": "completo", "unsupported": "sin respaldo"
}


def quality_numbers(review):
    numbers = {}

    for engine in ENGINES:
        entries = [e for e in review["entries"] if e["engine"] == engine]
        numbers[engine] = {}
        for key, title, categories in QUALITY:
            counts = {}
            for value, label, color, hatch in categories:
                counts[label] = sum(1 for e in entries if e[key].split(" (esperado")[0] == value)
            numbers[engine][key] = counts

    return numbers


def quality_chart(numbers):
    figure, axes = plt.subplots(3, 1, figsize=(8.2, 6.2))

    for axis, (key, title, categories) in zip(axes, QUALITY):
        for row, engine in enumerate(reversed(ENGINES)):
            left = 0
            for value, label, color, hatch in categories:
                count = numbers[engine][key][label]
                if count == 0:
                    continue
                axis.barh(row, count, left=left, height=0.55, color=color, edgecolor=SURFACE,
                          linewidth=2, hatch=hatch)
                text_color = "#ffffff" if color in ORDINAL[:2] else INK
                axis.text(left + count / 2, row, str(count), ha="center", va="center", fontsize=8.5,
                          color=text_color)
                left += count

        axis.set_yticks(range(len(ENGINES)), [ENGINE_LABELS[e] for e in reversed(ENGINES)])
        axis.set_xlim(0, 20)
        axis.set_title(title, loc="left", fontsize=10)
        axis.grid(axis="y", visible=False)
        handles = [plt.Rectangle((0, 0), 1, 1, facecolor=color, hatch=hatch, edgecolor="#ffffff")
                   for value, label, color, hatch in categories]
        axis.legend(handles, [LEGEND_LABELS[label] for value, label, color, hatch in categories], ncol=5,
                    loc="upper center", bbox_to_anchor=(0.5, -0.18), fontsize=8)

    figure.suptitle("Calidad del contexto y de las respuestas: valoración PRELIMINAR de IA, pendiente de revisión humana",
                    x=0.0, ha="left", fontsize=12, fontweight="bold", color=INK, y=1.01)
    figure.tight_layout(h_pad=2.2)
    note(figure, "Las barras cuentan ejecuciones (20 por motor), según reports/review/evaluation_review.json (versión 2). "
                 "La corrección se valora contra el relato y la respuesta esperada; el respaldo, solo contra el "
                 "contexto que el modelo recibió realmente. Las asignó una IA y no han sido validadas por una persona.")
    save(figure, "fig7_quality_preliminary.png")


def main():
    evaluation = load(EVALUATION)
    scaling = load(SCALING)
    review = load(REVIEW)

    runs = evaluation["results"]
    numbers = evaluation_numbers(runs)

    strip_chart(
        runs, lambda r: r["retrieval_timing"]["engine_reported_mean_ms"],
        "Tiempo de búsqueda por pregunta (con filtro de relato)", "Tiempo de búsqueda (ms, media de 5)",
        "fig1_retrieval_time.png",
        "Cada punto es una de las 20 preguntas (media de 5 repeticiones después de 1 calentamiento). Línea "
        "continua: media; punteada: mediana. Medido en un solo CPU con Python; los n-gramas de la búsqueda "
        "aproximada ya estaban en caché, y su tiempo depende sobre todo de si Levenshtein tuvo que corregir algún término.",
        lambda v: f"{v:.1f} ms")

    strip_chart(
        runs, lambda r: r["generation_time_ms"] / 1000,
        "Tiempo de generación de Qwen por pregunta (aparte de la búsqueda)", "Tiempo de generación (s)",
        "fig2_generation_time.png",
        "Una generación nueva por pregunta y motor con Qwen2.5-0.5B-Instruct en CPU (float32, sin muestreo). "
        "En estas ejecuciones la generación tardó entre 56 y 5,284 veces más que la búsqueda (mediana: 172 "
        "veces); la búsqueda fue como máximo el 1.7 % del total. Las generaciones más largas (RH06 con KMP y "
        "con Z) produjeron respuestas largas.",
        lambda v: f"{v:.1f} s")

    chunk_counts_chart(numbers)

    scaling_rows = scaling_numbers(scaling)

    scaling_chart(
        scaling_rows, "mean_ms", "Tiempo de búsqueda (ms, media)",
        "Tiempo de búsqueda frente al tamaño real de la colección (sin filtro de relato)", "fig4_scaling_time.png",
        "Subcolecciones reales de 1, 2 y 3 relatos, cada una con su propio índice y vocabulario. Cada orden "
        "usa las mismas preguntas (las de su relato base). Son solo tres tamaños y 6 o 7 preguntas por orden: "
        "la tendencia es orientativa, no una ley de crecimiento. KMP y Z examinan los mismos fragmentos; una "
        "posible razón de que Z sea más lento en esta implementación es que construye un arreglo Z sobre "
        "patrón + separador + texto por cada fragmento y término (no se midió por separado).")

    scaling_chart(
        scaling_rows, "examined_mean", "Fragmentos examinados (media)",
        "Fragmentos examinados frente al tamaño real de la colección (sin filtro de relato)", "fig5_scaling_examined.png",
        "La búsqueda exacta solo recorre los fragmentos que propone el índice invertido; KMP (punteado) y Z "
        "examinan exactamente los mismos, así que sus líneas coinciden. La búsqueda aproximada puntúa todos los "
        "fragmentos, así que su línea es igual al tamaño de la colección.", exact_identical=True)

    levenshtein_chart(scaling)

    quality = quality_numbers(review)
    quality_chart(quality)

    with open(FIGURES / "stage6_numbers.json", "w", encoding="utf-8") as file:
        json.dump({
            "evaluation": numbers,
            "scaling": scaling_rows,
            "scaling_collections": scaling["collections"],
            "quality_preliminary_ai": quality,
            "sources": {"evaluation": str(EVALUATION.relative_to(BASE_DIR)),
                        "scaling": str(SCALING.relative_to(BASE_DIR)),
                        "review": str(REVIEW.relative_to(BASE_DIR))}
        }, file, ensure_ascii=False, indent=2)

    print("saved", FIGURES / "stage6_numbers.json")


if __name__ == "__main__":
    main()
