from pathlib import Path
import pandas as pd

# ========= PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

AUTO_CSV = BASE_DIR / "results" / "tables" / "picos_scores.csv"
HUMAN_CSV = BASE_DIR / "evaluation" / "scoring_sheet.csv"
OUTPUT_CSV = BASE_DIR / "results" / "tables" / "picos_combined.csv"

# ========= INTEGRAÇÃO

def integrate_scores():
    if not AUTO_CSV.exists():
        raise FileNotFoundError("picos_scores.csv não encontrado.")

    if not HUMAN_CSV.exists():
        raise FileNotFoundError("scoring_sheet.csv não encontrado.")

    df_auto = pd.read_csv(AUTO_CSV)
    df_human = pd.read_csv(HUMAN_CSV)

    # Merge explícito por chaves experimentais
    df_combined = pd.merge(
        df_human,
        df_auto,
        on=["model", "prompt_version", "run_id"],
        how="left",
        validate="many_to_one"
    )

    df_combined.to_csv(OUTPUT_CSV, index=False)

    print(f"Arquivo integrado salvo em: {OUTPUT_CSV.relative_to(BASE_DIR)}")

# ========= ENTRY POINT

if __name__ == "__main__":
    integrate_scores()
