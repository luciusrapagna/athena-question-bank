from pathlib import Path
from tkinter import Tk, filedialog
from pypdf import PdfReader

from src.database.db import criar_tabelas, salvar_documento

def selecionar_pdf():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    arquivo = filedialog.askopenfilename(
        title="Selecione uma prova em PDF",
        filetypes=[
            ("PDF", "*.pdf"),
            ("Todos os arquivos", "*.*")
        ]
    )

    root.destroy()
    return arquivo

def extrair_texto_pdf(caminho_pdf):
    reader = PdfReader(caminho_pdf)
    textos = []

    for pagina in reader.pages:
        texto = pagina.extract_text()
        if texto:
            textos.append(texto)

    return "\n\n".join(textos)

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

    print("PDF importado e salvo no banco com sucesso.")

if __name__ == "__main__":
    importar_pdf()
