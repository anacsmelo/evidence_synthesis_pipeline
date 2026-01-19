import pdfplumber
from pathlib import Path

# ========= CONFIGURAÇÕES

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "sources" / "articles_pdf"
OUTPUT_DIR = BASE_DIR / "data" / "sources" / "extracted_text"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========  FUNÇÕES

def clean_text(text: str) -> str:
    """
    Limpeza mínima e padronizada:
    - Remove múltiplos espaços
    - Remove linhas vazias excessivas
    - Não altera conteúdo semântico
    """
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join([line for line in lines if line])
    return cleaned


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extração sequencial de todas as páginas do PDF.
    Não reordena blocos, não interpreta layout.
    """
    extracted_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(
                    f"\n--- Page {page_number} ---\n{page_text}"
                )

    return "\n".join(extracted_pages)


def process_all_pdfs():
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("Nenhum PDF encontrado em articles_pdf.")

    for pdf_path in pdf_files:
        print(f"Extraindo: {pdf_path.name}")

        raw_text = extract_pdf_text(pdf_path)
        cleaned_text = clean_text(raw_text)

        output_file = OUTPUT_DIR / f"{pdf_path.stem}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Salvo em: {output_file.relative_to(BASE_DIR)}")

    print("Extração finalizada com sucesso.")

# ========= ENTRY POINT

if __name__ == "__main__":
    process_all_pdfs()
