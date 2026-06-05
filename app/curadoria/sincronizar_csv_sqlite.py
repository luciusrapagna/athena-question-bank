import sqlite3
import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/banco_questoes/banco_questoes.csv")
DB_PATH = "app/db/planos_aula.db"

MAP = {
    "area": "grande_area",
    "assunto": "tema",
    "competencia": "competencia",
    "enunciado": "enunciado",
    "alternativa_a": "alternativa_a",
    "alternativa_b": "alternativa_b",
    "alternativa_c": "alternativa_c",
    "alternativa_d": "alternativa_d",
    "alternativa_e": "alternativa_e",
    "gabarito": "gabarito",
    "fonte": "fonte",
    "ano": "ano",
    "arquivo_origem": "arquivo_origem",
}

def main():
    df = pd.read_csv(CSV_PATH)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("DELETE FROM questoes")

    inseridas = 0

    for _, row in df.iterrows():
        dados = {}
        for origem, destino in MAP.items():
            dados[destino] = row[origem] if origem in df.columns and pd.notna(row[origem]) else None

        cur.execute("""
            INSERT INTO questoes (
                grande_area, tema, competencia, enunciado,
                alternativa_a, alternativa_b, alternativa_c,
                alternativa_d, alternativa_e, gabarito,
                fonte, ano, arquivo_origem
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["grande_area"], dados["tema"], dados["competencia"], dados["enunciado"],
            dados["alternativa_a"], dados["alternativa_b"], dados["alternativa_c"],
            dados["alternativa_d"], dados["alternativa_e"], dados["gabarito"],
            dados["fonte"], dados["ano"], dados["arquivo_origem"]
        ))

        inseridas += 1

    con.commit()
    con.close()

    print(f"CSV lido: {CSV_PATH}")
    print(f"Questões sincronizadas no SQLite: {inseridas}")

if __name__ == "__main__":
    main()
