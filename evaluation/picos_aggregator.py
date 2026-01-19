from pathlib import Path
import pandas as pd

from picos_parser import parse_file

# ========= PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

LLM_OUTPUTS_DIR = BASE_DIR / "data" / "llm_outputs"
RESULTS_DIR = BASE_DIR / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = RESULTS_DIR / "picos_scores.csv"

# ========= FUNÇÕES AUXILIARES

def parse_filename(file_path: Path):
    """
    Extrai metadados básicos a partir do nome do arquivo.
    Esperado: <prompt>_run<id>.md
    """
    name = file_path.stem

    if "_run" in name:
        prompt, run = name.split("_run")
        run_id = int(run)
    else:
        prompt = name
        run_id = None

    return prompt, run_id


def aggregate_picos():
    rows = []

    model_dirs = [d for d in LLM_OUTPUTS_DIR.iterdir() if d.is_dir()]

    if not model_dirs:
        raise FileNotFoundError("Nenhum diretório de outputs encontrado.")

    for model_dir in model_dirs:
        model_name = model_dir.name

        for md_file in model_dir.glob("*.md"):
            prompt_version, run_id = parse_filename(md_file)

            parsed = parse_file(md_file)

            row = {
                "model": model_name,
                "prompt_version": prompt_version,
                "run_id": run_id
            }

            total_score = 0

            for component, result in parsed.items():
                score = result["score"]
                row[f"{component}_score"] = score
                row[f"{component}_explicit"] = result["explicit_section"]
                total_score += score

            row["total_picos_score"] = total_score

            rows.append(row)

    df = pd.DataFrame(rows)

    df.sort_values(
        by=["model", "prompt_version", "run_id"],
        inplace=True
    )

    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Arquivo agregado salvo em: {OUTPUT_CSV.relative_to(BASE_DIR)}")

# =========  ENTRY POINT

if __name__ == "__main__":
    aggregate_picos()
