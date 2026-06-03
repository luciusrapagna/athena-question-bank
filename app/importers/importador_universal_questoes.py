from pathlib import Path
import sqlite3
import pandas as pd

from tkinter import Tk
from tkinter.filedialog import askopenfilename

DB_PATH = "app/db/planos_aula.db"


MAPEAMENTO = {
    "instituicao": ["instituicao","instituição"],
    "ano": ["ano"],
    "prova": ["prova"],
    "grande_area": ["grande_area","área","area"],
    "subarea": ["subarea","subárea"],
    "tema": ["tema","assunto"],
    "enunciado": ["enunciado","pergunta","questao","questão"],
    "alternativa_a": ["a"],
    "alternativa_b": ["b"],
    "alternativa_c": ["c"],
    "alternativa_d": ["d"],
    "alternativa_e": ["e"],
    "gabarito": ["gabarito","resposta"]
}


def selecionar_arquivo():
    root = Tk()
    root.withdraw()

    return askopenfilename(
        title="Selecione banco de questões",
        filetypes=[
            ("Planilhas", "*.xlsx *.xls *.csv")
        ]
    )


def normalizar(nome):
    return (
        nome.lower()
        .strip()
        .replace(" ", "_")
    )


def descobrir_coluna(colunas, aliases):

    for coluna in colunas:

        c = normalizar(coluna)

        for alias in aliases:

            if c == normalizar(alias):
                return coluna

    return None


def importar():

    arquivo = selecionar_arquivo()

    if not arquivo:
        print("Nenhum arquivo selecionado.")
        return

    ext = Path(arquivo).suffix.lower()

    if ext == ".csv":
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    colunas = list(df.columns)

    encontrados = {}

    for campo, aliases in MAPEAMENTO.items():
        encontrados[campo] = descobrir_coluna(
            colunas,
            aliases
        )

    total = 0

    for _, row in df.iterrows():

        cur.execute("""
        INSERT INTO questoes (
            instituicao,
            ano,
            prova,
            grande_area,
            subarea,
            tema,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            alternativa_e,
            gabarito
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row.get(encontrados["instituicao"]),
            row.get(encontrados["ano"]),
            row.get(encontrados["prova"]),
            row.get(encontrados["grande_area"]),
            row.get(encontrados["subarea"]),
            row.get(encontrados["tema"]),
            row.get(encontrados["enunciado"]),
            row.get(encontrados["alternativa_a"]),
            row.get(encontrados["alternativa_b"]),
            row.get(encontrados["alternativa_c"]),
            row.get(encontrados["alternativa_d"]),
            row.get(encontrados["alternativa_e"]),
            row.get(encontrados["gabarito"])
        ))

        total += 1

    cur.execute(
        """
        INSERT INTO importacoes_questoes
        (
            arquivo,
            total_registros
        )
        VALUES (?, ?)
        """,
        (arquivo, total)
    )

    con.commit()
    con.close()

    print(f"{total} questões importadas.")


if __name__ == "__main__":
    importar()
