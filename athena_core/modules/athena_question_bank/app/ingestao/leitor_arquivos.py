from pathlib import Path
from docx import Document
from pypdf import PdfReader


def ler_txt_md(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8", errors="ignore")


def ler_docx(caminho: Path) -> str:
    documento = Document(caminho)
    textos = []

    for paragrafo in documento.paragraphs:
        if paragrafo.text.strip():
            textos.append(paragrafo.text.strip())

    return "\n".join(textos)


def ler_pdf(caminho: Path) -> str:
    leitor = PdfReader(str(caminho))
    textos = []

    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            textos.append(texto)

    return "\n".join(textos)


def ler_arquivo(caminho: Path) -> str:
    extensao = caminho.suffix.lower()

    if extensao in [".txt", ".md"]:
        return ler_txt_md(caminho)

    if extensao == ".docx":
        return ler_docx(caminho)

    if extensao == ".pdf":
        return ler_pdf(caminho)

    return ""
