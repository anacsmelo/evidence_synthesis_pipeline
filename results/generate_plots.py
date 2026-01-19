from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ========= CONFIG. ABNT
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 10
})

# ========= PATHS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "results" / "tables" / "picos_combined.csv"
FIGURES_DIR = BASE_DIR / "results" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# =========  MAPA DE NOMES DE MODELOS

MODEL_LABELS = {
    "deepseek_deepseek-r1-0528:free": "DeepSeek R1",
    "openai_gpt-oss-120b:free": "GPT-OSS-120B",
    "qwen_qwen3-4b:free": "Qwen 3 4B"
}

# ========= LOAD DATA

df = pd.read_csv(DATA_FILE)

# Aplicando simplificação de nomenclatura
df["model_label"] = df["model"].map(MODEL_LABELS)

# =========  1. BOX PLOT — TOTAL PICOS SCORE POR MODELO
fig, ax = plt.subplots(figsize=(7, 4.5))

df.boxplot(
    column="total_picos_score",
    by="model_label",
    ax=ax
)

ax.set_title("Distribuição do Score PICOS Total por Modelo")
ax.set_xlabel("Modelo")
ax.set_ylabel("Score PICOS Total")

plt.suptitle("")  # remove título automático do pandas
plt.xticks(rotation=15)
plt.tight_layout()

plt.savefig(FIGURES_DIR / "boxplot_total_picos_by_model.png", dpi=300)
plt.close()

# =========  2. MÉDIA DE CADA COMPONENTE PICOS POR MODELO
components = [
    "population_score",
    "intervention_score",
    "comparator_score",
    "outcomes_score",
    "study_design_score"
]

component_labels = {
    "population_score": "Population",
    "intervention_score": "Intervention",
    "comparator_score": "Comparator",
    "outcomes_score": "Outcomes",
    "study_design_score": "Study design"
}

mean_components = (
    df
    .groupby("model_label")[components]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))

x = range(len(mean_components))
width = 0.15

for i, comp in enumerate(components):
    ax.bar(
        [p + i * width for p in x],
        mean_components[comp],
        width,
        label=component_labels[comp]
    )

ax.set_xticks([p + 2 * width for p in x])
ax.set_xticklabels(mean_components["model_label"])
ax.set_xlabel("Modelo")
ax.set_ylabel("Score Médio")
ax.set_title("Média dos Componentes PICOS por Modelo")

ax.legend(
    title="Componente",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False
)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "mean_picos_components_by_model.png", dpi=300)
plt.close()

# ========= 3. TAXA DE COMPLETUDE PICOS (SCORE == 2)
completeness = (
    df
    .groupby("model_label")[components]
    .apply(lambda x: (x == 2).mean())
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))

x = range(len(completeness))
width = 0.15

for i, comp in enumerate(components):
    ax.bar(
        [p + i * width for p in x],
        completeness[comp],
        width,
        label=component_labels[comp]
    )

ax.set_xticks([p + 2 * width for p in x])
ax.set_xticklabels(completeness["model_label"])
ax.set_xlabel("Modelo")
ax.set_ylabel("Proporção")
ax.set_title("Proporção de Componentes PICOS Completos (Score = 2)")

ax.legend(
    title="Componente",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False
)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "picos_completeness_rate.png", dpi=300)
plt.close()

# ========= 4. CORRELAÇÃO PARSER × AVALIAÇÃO HUMANA (SE EXISTIR)
df["human_mean"] = df[["clarity", "fidelity"]].mean(axis=1)

fig, ax = plt.subplots(figsize=(6, 4.5))

ax.scatter(
    df["total_picos_score"],
    df["human_mean"]
)

r = df["total_picos_score"].corr(df["human_mean"])

ax.set_xlabel("Score PICOS Total (Automático)")
ax.set_ylabel("Score Médio Humano")
ax.set_title(f"Correlação Parser PICOS × Avaliação Humana (r = {r:.2f})")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "parser_vs_human_correlation.png", dpi=300)
plt.close()

print("Gráficos gerados com sucesso.")
