import sqlite3
import pandas as pd
from pathlib import Path
from tkinter import Tk, filedialog

DB_PATH = Path("database/question_bank.db")

def selecionar_excel():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    arquivo = filedialog.askopenfilename(
        title="Selecione a planilha de curadoria",
        filetypes=[
            ("Excel", "*.xlsx"),
            ("Todos os arquivos", "*.*")
        ]
    )

    root.destroy()
    return arquivo

arquivo = selecionar_excel()

if not arquivo:
    print("Nenhum arquivo selecionado.")
    raise SystemExit

df = pd.read_excel(arquivo)

colunas_obrigatorias = ["id", "area", "subarea", "tema", "competencia", "periodo"]

for col in colunas_obrigatorias:
    if col not in df.columns:
        print(f"Coluna ausente: {col}")
        raise SystemExit

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for _, row in df.iterrows():
    cur.execute("""
    UPDATE questoes_extraidas
    SET
        area = ?,
        subarea = ?,
        tema = ?,
        competencia = ?,
        periodo = ?,
        status_revisao = 'revisado'
    WHERE id = ?
    """, (
        str(row.get("area", "")).strip(),
        str(row.get("subarea", "")).strip(),
        str(row.get("tema", "")).strip(),
        str(row.get("competencia", "")).strip(),
        str(row.get("periodo", "")).strip(),
        int(row["id"])
    ))

conn.commit()
conn.close()

print("Curadoria importada com sucesso.")
