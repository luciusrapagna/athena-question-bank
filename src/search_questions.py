import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("database/question_bank.db")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

termo = input("Digite área, subárea, tema, competência ou palavra do enunciado: ").strip()

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    qe.id,
    qe.numero_questao,
    qe.area,
    qe.subarea,
    qe.tema,
    qe.competencia,
    qe.periodo,
    substr(qe.texto_questao, 1, 500) AS previa,
    d.prova,
    d.instituicao,
    d.ano
FROM questoes_extraidas qe
LEFT JOIN documentos d ON qe.documento_id = d.id
WHERE
    qe.area LIKE ?
    OR qe.subarea LIKE ?
    OR qe.tema LIKE ?
    OR qe.competencia LIKE ?
    OR qe.periodo LIKE ?
    OR qe.texto_questao LIKE ?
ORDER BY d.ano DESC, CAST(qe.numero_questao AS INTEGER)
"""

param = f"%{termo}%"
df = pd.read_sql_query(query, conn, params=[param, param, param, param, param, param])
conn.close()

print(f"\nQuestões encontradas: {len(df)}")

if len(df) > 0:
    print(df[["id", "numero_questao", "area", "subarea", "tema", "prova", "ano"]].to_string(index=False))

    saida = OUTPUT_DIR / f"busca_{termo.replace(' ', '_')}.xlsx"
    df.to_excel(saida, index=False)
    print(f"\nResultado exportado: {saida}")
else:
    print("Nenhuma questão encontrada.")
