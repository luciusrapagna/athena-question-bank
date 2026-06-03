import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def validar(texto):
    texto = texto or ""

    tem_abcd = all(alt in texto for alt in ["(A)", "(B)", "(C)", "(D)"])

    duplicada = any(texto.count(alt) > 1 for alt in ["(A)", "(B)", "(C)", "(D)"])

    cabecalho = "Núcleo Mineiro" in texto or "Teste de Progresso" in texto

    if tem_abcd and not duplicada and not cabecalho and len(texto) > 120:
        return "valida"

    return "revisar_manual"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE questoes_extraidas ADD COLUMN qualidade TEXT")
except Exception:
    pass

cur.execute("SELECT id, texto_questao FROM questoes_extraidas")
questoes = cur.fetchall()

for qid, texto in questoes:
    qualidade = validar(texto)
    cur.execute(
        "UPDATE questoes_extraidas SET qualidade = ? WHERE id = ?",
        (qualidade, qid)
    )

conn.commit()

cur.execute("SELECT qualidade, COUNT(*) FROM questoes_extraidas GROUP BY qualidade")
print(cur.fetchall())

conn.close()
