from pathlib import Path
from tkinter import Tk, filedialog

from src.database.db import criar_tabelas, salvar_documento
from src.reader.smart_pdf_reader import ler_pdf_inteligente

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

    resultado = ler_pdf_inteligente(caminho_pdf)

    perfil = resultado["perfil"]
    texto = resultado["texto"]
    questoes = resultado["questoes"]

    print(f"Perfil detectado: {perfil}")
    print(f"Questões detectadas no leitor inteligente: {len(questoes)}")

    salvar_documento(
        tipo=f"prova_pdf_{perfil}",
        prova=prova,
        instituicao=instituicao,
        ano=ano,
        arquivo_origem=str(Path(caminho_pdf)),
        texto_bruto=texto
    )

    print("PDF importado com leitor inteligente e salvo no banco.")

if __name__ == "__main__":
    importar_pdf()
