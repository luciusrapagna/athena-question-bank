import shutil
from pathlib import Path
from tkinter import Tk, filedialog
from app.config_paths import DIR_PROVAS_ENTRADA, DIR_PLANOS_ENTRADA


def selecionar_arquivos(titulo):
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    arquivos = filedialog.askopenfilenames(
        title=titulo,
        filetypes=[
            ("Arquivos de texto, Word e PDF", "*.txt *.md *.docx *.pdf"),
            ("Todos os arquivos", "*.*"),
        ],
    )

    root.destroy()
    return arquivos


def copiar_arquivos(arquivos, destino):
    destino.mkdir(parents=True, exist_ok=True)

    copiados = []

    for arquivo in arquivos:
        origem = Path(arquivo)
        saida = destino / origem.name
        shutil.copy2(origem, saida)
        copiados.append(saida)

    return copiados


def main():
    print("ATHENA QUESTION BANK - IMPORTADOR PELO EXPLORER")
    print("1 - Inserir provas ENADE/ENARE/ENAMED")
    print("2 - Inserir planos de aula")

    opcao = input("Escolha uma opção: ").strip()

    if opcao == "1":
        arquivos = selecionar_arquivos("Selecione as provas ENADE, ENARE ou ENAMED")
        copiados = copiar_arquivos(arquivos, DIR_PROVAS_ENTRADA)
        print(f"Provas copiadas: {len(copiados)}")
        for item in copiados:
            print(item)

    elif opcao == "2":
        arquivos = selecionar_arquivos("Selecione os planos de aula")
        copiados = copiar_arquivos(arquivos, DIR_PLANOS_ENTRADA)
        print(f"Planos copiados: {len(copiados)}")
        for item in copiados:
            print(item)

    else:
        print("Opção inválida.")


if __name__ == "__main__":
    main()
