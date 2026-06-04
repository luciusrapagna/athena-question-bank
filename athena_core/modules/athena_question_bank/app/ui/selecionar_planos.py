from tkinter import Tk
from tkinter.filedialog import askopenfilenames

def selecionar_arquivos():

    root = Tk()
    root.withdraw()

    arquivos = askopenfilenames(
        title="Selecione os Planos de Aula",
        filetypes=[
            ("Documentos", "*.docx *.pdf *.xlsx")
        ]
    )

    return list(arquivos)

if __name__ == "__main__":

    arquivos = selecionar_arquivos()

    for arq in arquivos:
        print(arq)