import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("database/question_bank.db")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    qe.id,
    qe.documento_id,
    qe.numero_questao,
    qe.texto_questao,
    qe.status_revisao,
    qe.area,
    qe.subarea,
    qe.tema,
    qe.competencia,
    qe.periodo,
    d.prova,
    d.instituicao,
    d.ano,
    d.arquivo_origem
FROM questoes_extraidas qe
LEFT JOIN documentos d ON qe.documento_id = d.id
ORDER BY qe.documento_id, CAST(qe.numero_questao AS INTEGER)
"""

try:
    df = pd.read_sql_query(query, conn)
except Exception:
    cur = conn.cursor()
    for col in ["area", "subarea", "tema", "competencia", "periodo"]:
        try:
            cur.execute(f"ALTER TABLE questoes_extraidas ADD COLUMN {col} TEXT")
        except Exception:
            pass
    conn.commit()
    df = pd.read_sql_query(query, conn)

conn.close()

saida = OUTPUT_DIR / "questoes_extraidas_para_curadoria.xlsx"
df.to_excel(saida, index=False)

print(f"Arquivo exportado com sucesso: {saida}")
