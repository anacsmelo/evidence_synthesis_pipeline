from pathlib import Path

# ========= PATHS

BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = BASE_DIR / "data" / "sources" / "extracted_text"
OUTPUT_FILE = BASE_DIR / "data" / "sources" / "corpus_compiled.md"

# ========= FUNÇÕES

def build_corpus():
    txt_files = sorted(EXTRACTED_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError("Nenhum arquivo .txt encontrado em extracted_text.")

    corpus_sections = []

    for idx, txt_path in enumerate(txt_files, start=1):
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        section = f"""
## Study {idx}
Source file: {txt_path.name}

{content}
"""
        corpus_sections.append(section)

    final_corpus = "\n\n".join(corpus_sections)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_corpus.strip())

    print(f"Corpus compilado salvo em: {OUTPUT_FILE.relative_to(BASE_DIR)}")

# ========= ENTRY POINT

if __name__ == "__main__":
    build_corpus()
