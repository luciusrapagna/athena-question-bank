from pathlib import Path
from tkinter import Tk, filedialog
import fitz

from src.database.db import criar_tabelas, salvar_documento

def selecionar_pdf():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    arquivo = filedialog.askopenfilename(
        title="Selecione uma prova em PDF",
        filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
    )

    root.destroy()
    return arquivo

def extrair_texto_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    paginas = []

    for page in doc:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (round(b[1] / 10) * 10, b[0]))

        texto_pagina = []
        for b in blocks:
            txt = b[4].strip()
            if txt:
                texto_pagina.append(txt)

        paginas.append("\n".join(texto_pagina))

    return "\n\n".join(paginas)

def importar_pdf():
    criar_tabelas()

    caminho_pdf = selecionar_pdf()

    if not caminho_pdf:
        print("Nenhum arquivo selecionado.")
        return

    print(f"Arquivo selecionado: {caminho_pdf}")

    prova = input("Nome da prova: ")
    instituicao = input("Instituição/Fonte: ")
    ano = input("Ano: ")

    try:
        ano = int(ano)
    except ValueError:
        ano = None

    texto = extrair_texto_pdf(caminho_pdf)

    salvar_documento(
        tipo="prova_pdf",
        prova=prova,
        instituicao=instituicao,
        ano=ano,
        arquivo_origem=str(Path(caminho_pdf)),
        texto_bruto=texto
    )

    print("PDF importado com extração aprimorada e salvo no banco.")

if __name__ == "__main__":
    importar_pdf()
