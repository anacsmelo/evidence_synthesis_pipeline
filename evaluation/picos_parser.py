import re
from pathlib import Path
from typing import Dict

# ========= DEFINIÇÕES PICOS

PICOS_COMPONENTS = {
    "population": {
        "label": "Population",
        "keywords": ["population", "patients", "subjects", "participants"]
    },
    "intervention": {
        "label": "Intervention",
        "keywords": ["intervention", "treatment", "therapy", "procedure"]
    },
    "comparator": {
        "label": "Comparator",
        "keywords": ["comparator", "control", "placebo", "comparison"]
    },
    "outcomes": {
        "label": "Outcomes",
        "keywords": ["outcome", "endpoint", "measure", "result"]
    },
    "study_design": {
        "label": "Study design",
        "keywords": ["study design", "randomized", "controlled", "trial", "cohort"]
    }
}

# ========= FUNÇÕES DE PARSE

def extract_section(text: str, section_label: str) -> str:
    """
    Extrai o conteúdo textual de uma seção explícita do tipo:
    'Population:' até a próxima seção.
    """
    pattern = rf"{section_label}\s*:\s*(.*?)(?=\n[A-Z][a-zA-Z\s]+:|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def keyword_presence(text: str, keywords: list) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def score_component(section_text: str, fallback_text: str, keywords: list) -> int:
    """
    Retorna:
    2 = seção explícita e não vazia
    1 = não estruturada, mas keywords presentes
    0 = ausente
    """
    if section_text and len(section_text.split()) >= 10:
        return 2

    if keyword_presence(fallback_text, keywords):
        return 1

    return 0


def parse_picos(text: str) -> Dict[str, Dict]:
    """
    Parser principal PICOS.
    """
    results = {}

    for key, meta in PICOS_COMPONENTS.items():
        section_text = extract_section(text, meta["label"])
        score = score_component(
            section_text=section_text,
            fallback_text=text,
            keywords=meta["keywords"]
        )

        results[key] = {
            "score": score,
            "explicit_section": bool(section_text),
            "word_count": len(section_text.split()) if section_text else 0
        }

    return results

## ========= AUXILIAR

def parse_file(file_path: Path) -> Dict[str, Dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return parse_picos(text)


# ========= EXECUÇÃO SIMPLES

if __name__ == "__main__":
    example_file = Path("data/llm_outputs/example.md")

    if example_file.exists():
        parsed = parse_file(example_file)
        for component, result in parsed.items():
            print(component, result)
    else:
        print("Arquivo de exemplo não encontrado.")
