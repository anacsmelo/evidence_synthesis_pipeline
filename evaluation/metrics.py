from pathlib import Path
import pandas as pd
import json
import sys

# =========  PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

PICOS_SCORES = BASE_DIR / "results" / "tables" / "picos_scores.csv"
METADATA_LOG = BASE_DIR / "experiments" / "metadata_log.json"
OUTPUT_DIR = BASE_DIR / "results" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "metrics_by_model_prompt.csv"

# ========= AUXILIARES

def normalize_model_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    name = name.replace(":free", "")
    name = name.split("/")[-1]
    return name.strip()

# ========= EXECUÇÃO

def main():
    print("Iniciando cálculo de métricas...")

    if not PICOS_SCORES.exists():
        print("ERRO: picos_scores.csv não encontrado.")
        sys.exit(1)

    if not METADATA_LOG.exists():
        print("ERRO: metadata_log.json não encontrado.")
        sys.exit(1)

    # ---------- LOAD DATA

    df_picos = pd.read_csv(PICOS_SCORES)

    with open(METADATA_LOG, "r", encoding="utf-8") as f:
        df_meta = pd.DataFrame(json.load(f))

    print(f"Registros PICOS automáticos: {len(df_picos)}")
    print(f"Registros de metadata: {len(df_meta)}")

    if df_picos.empty:
        print("AVISO: picos_scores.csv está vazio.")
        sys.exit(0)

    # ---------- NORMALIZAÇÃO

    df_picos["model"] = df_picos["model"].apply(normalize_model_name)
    df_meta["model"] = df_meta["model"].apply(normalize_model_name)

    df_picos["prompt_version"] = df_picos["prompt_version"].astype(str).str.strip()
    df_meta["prompt_version"] = df_meta["prompt_version"].astype(str).str.strip()

    df_picos["run_id"] = df_picos["run_id"].astype(int)
    df_meta["run_id"] = df_meta["run_id"].astype(int)

    # ---------- METRICA 1 — TAXA DE GERAÇÃO VÁLIDA

    gen_rate = (
        df_meta
        .groupby(["model", "prompt_version"])["has_text_output"]
        .mean()
        .reset_index(name="valid_generation_rate")
    )

    # ---------- METRICA 2 — SCORE PICOS MÉDIO

    picos_components = [
        "population_score",
        "intervention_score",
        "comparator_score",
        "outcomes_score",
        "study_design_score"
    ]

    score_means = (
        df_picos
        .groupby(["model", "prompt_version"])
        [picos_components + ["total_picos_score"]]
        .mean()
        .reset_index()
    )

    # ---------- METRICA 3 — TAXA DE COMPLETUDE (SCORE == 2)

    completeness = (
        (df_picos[picos_components] == 2)
        .groupby([df_picos["model"], df_picos["prompt_version"]])
        .mean()
        .reset_index()
    )

    # ---------- METRICA 4 — VARIABILIDADE INTRA-MODELO

    variability = (
        df_picos
        .groupby(["model", "prompt_version"])["total_picos_score"]
        .std()
        .reset_index(name="total_score_std")
    )

    # ---------- MERGE FINAL (BASE = PICOS)

    df_metrics = (
        score_means
        .merge(completeness, on=["model", "prompt_version"], how="left", suffixes=("", "_completeness"))
        .merge(variability, on=["model", "prompt_version"], how="left")
        .merge(gen_rate, on=["model", "prompt_version"], how="left")
    )

    print(f"Métricas calculadas: {len(df_metrics)} linhas")

    # ---------- EXPORTAR

    df_metrics.to_csv(OUTPUT_FILE, index=False)
    print(f"Arquivo salvo em: {OUTPUT_FILE}")

# ========= ENTRY POINT

if __name__ == "__main__":
    main()
