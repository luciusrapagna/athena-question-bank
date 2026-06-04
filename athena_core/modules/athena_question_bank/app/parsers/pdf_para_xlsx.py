from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


def selecionar_pdf():

    root = Tk()
    root.withdraw()

    arquivo = askopenfilename(
        title="Selecione a prova em PDF",
        filetypes=[
            ("PDF", "*.pdf")
        ]
    )

    return arquivo


def extrair_texto_pdf(caminho_pdf):

    reader = PdfReader(caminho_pdf)

    texto = []

    for pagina in reader.pages:

        conteudo = pagina.extract_text()

        if conteudo:
            texto.append(conteudo)

    return "\n".join(texto)


def salvar_xlsx(texto, pdf):

    output_dir = Path("outputs")

    output_dir.mkdir(exist_ok=True)

    nome = Path(pdf).stem

    arquivo_saida = output_dir / f"{nome}.xlsx"

    df = pd.DataFrame(
        {
            "texto": texto.split("\n")
        }
    )

    df.to_excel(
        arquivo_saida,
        index=False
    )

    return arquivo_saida


def main():

    pdf = selecionar_pdf()

    if not pdf:
        print("Nenhum PDF selecionado.")
        return

    print("PDF selecionado:")
    print(pdf)

    texto = extrair_texto_pdf(pdf)

    arquivo_saida = salvar_xlsx(
        texto,
        pdf
    )

    print()
    print("Arquivo gerado:")
    print(arquivo_saida)


if __name__ == "__main__":
    main()