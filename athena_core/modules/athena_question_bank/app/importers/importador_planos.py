from pathlib import Path
import sqlite3
import pandas as pd
from docx import Document
from pypdf import PdfReader
from app.ui.selecionar_planos import selecionar_arquivos

DB_PATH = Path("app/db/planos_aula.db")


def ler_docx(caminho):
    doc = Document(caminho)
    textos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(textos)


def ler_pdf(caminho):
    reader = PdfReader(caminho)
    textos = []
    for page in reader.pages:
        texto = page.extract_text()
        if texto:
            textos.append(texto)
    return "\n".join(textos)


def ler_xlsx(caminho):
    abas = pd.read_excel(caminho, sheet_name=None)
    textos = []
    for nome_aba, df in abas.items():
        textos.append(f"ABA: {nome_aba}")
        textos.append(df.astype(str).to_string(index=False))
    return "\n".join(textos)


def ler_arquivo(caminho):
    ext = Path(caminho).suffix.lower()

    if ext == ".docx":
        return ler_docx(caminho)
    if ext == ".pdf":
        return ler_pdf(caminho)
    if ext == ".xlsx":
        return ler_xlsx(caminho)

    raise ValueError(f"Formato não suportado: {ext}")


def salvar_plano(caminho, conteudo):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO planos_aula (
            disciplina,
            modulo,
            periodo,
            aula,
            data_aula,
            objetivos,
            conteudo,
            metodologia,
            referencia,
            arquivo_origem
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            None,
            None,
            None,
            Path(caminho).stem,
            None,
            None,
            conteudo,
            None,
            None,
            str(caminho),
        ),
    )

    con.commit()
    con.close()


def importar_planos():
    arquivos = selecionar_arquivos()

    if not arquivos:
        print("Nenhum arquivo selecionado.")
        return

    for caminho in arquivos:
        print(f"Importando: {caminho}")
        conteudo = ler_arquivo(caminho)
        salvar_plano(caminho, conteudo)
        print("Plano salvo no banco.")

    print("Importação concluída.")


if __name__ == "__main__":
    importar_planos()
