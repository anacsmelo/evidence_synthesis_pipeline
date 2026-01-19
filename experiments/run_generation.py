import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ========= PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = DATA_DIR / "prompts"
OUTPUT_DIR = DATA_DIR / "llm_outputs"

SOURCES_DIR = DATA_DIR / "sources"
CORPUS_FILE = SOURCES_DIR / "corpus_compiled.md"

EXPERIMENTS_DIR = BASE_DIR / "experiments"
CONFIG_FILE = EXPERIMENTS_DIR / "configs.yaml"
METADATA_FILE = EXPERIMENTS_DIR / "metadata_log.json"

# ========= OPENROUTER CLIENT

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY não definida.")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# =========  FUNCOES AUXILIARES

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_corpus() -> str:
    if not CORPUS_FILE.exists():
        raise FileNotFoundError("corpus_compiled.md não encontrado. Execute build_corpus.py")
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        return f.read()

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def save_output(model_slug: str, prompt_name: str, run_id: int, text: str) -> str:
    model_dir = OUTPUT_DIR / model_slug
    ensure_dir(model_dir)

    output_path = model_dir / f"{prompt_name}_run{run_id}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return str(output_path)

def append_metadata(entry: dict):
    data = []

    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            # Arquivo existe mas está vazio ou inválido → recomeça
            data = []

    data.append(entry)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ========= CHAMADA AO MODELO

def generate_synthesis(model_name: str, full_prompt: str, temperature: float, max_tokens: int):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um pesquisador em Engenharia Biomédica."
                    "Gere uma síntese de evidência estruturada EXCLUSIVAMENTE"
                    "segundo o framework PICOS (Population, Intervention, Comparator, Outcomes, Study design)."
                    "Não explique seu raciocínio."
                    "Não utilize conhecimento externo."
                    "Não inclua conteúdo fora das seções PICOS."
                )
            },
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response

# =========  EXECUÇÃO

def main():
    config = load_config()
    corpus_text = load_corpus()

    temperature = config.get("temperature", 0.2)
    runs_per_model = config.get("runs_per_model", 1)

    prompt_files = sorted(PROMPTS_DIR.glob("*.txt"))
    if not prompt_files:
        raise FileNotFoundError("Nenhum prompt encontrado em data/prompts.")

    for model_cfg in config["models"]:
        provider = model_cfg["provider"]
        model_name = model_cfg["name"]
        model_slug = model_name.replace("/", "_")

        max_tokens = model_cfg["max_tokens"]

        for prompt_path in prompt_files:
            prompt_name = prompt_path.stem
            prompt_text = load_prompt(prompt_path)

            full_prompt = f"""
{prompt_text}

--- CORPUS DE ESTUDOS ---
{corpus_text}
"""

            for run_id in range(1, runs_per_model + 1):
                print(f"Modelo: {model_name} | Prompt: {prompt_name} | Run: {run_id}")

                response = generate_synthesis(
                    model_name=model_name,
                    full_prompt=full_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                if response is None or not hasattr(response, "choices") or not response.choices:
                    content = (
                        "### NO RESPONSE RETURNED BY MODEL\n\n"
                        "The API did not return a valid completion object.\n"
                        "This execution is preserved for methodological analysis.\n"
                        )
                    finish_reason = "no_response"
                    has_text_output = False
                else:
                    choice = response.choices[0]
                    content = choice.message.content or ""
                    finish_reason = choice.finish_reason
                    has_text_output = bool(content.strip())

                    if not has_text_output:
                        content = (
                            "### NO TEXT OUTPUT GENERATED\n\n"
                            "- finish_reason: {finish_reason}\n"
                            "This execution is preserved for methodological analysis.\n"
                        )

                output_file = save_output(
                    model_slug=model_slug,
                    prompt_name=prompt_name,
                    run_id=run_id,
                    text=content
                )

                metadata = {
                    "timestamp_utc": datetime.utcnow().isoformat(),
                    "provider": provider,
                    "model": model_name,
                    "prompt_version": prompt_name,
                    "run_id": run_id,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "finish_reason": finish_reason,
                    "has_text_output": has_text_output,
                    "corpus_file": str(CORPUS_FILE),
                    "output_file": output_file
                }

                append_metadata(metadata)

    print("Geração concluída com sucesso.")

# ========= ENTRY POINT

if __name__ == "__main__":
    main()
