import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def validar(texto):
    texto = texto or ""

    tem_a = "(A)" in texto
    tem_b = "(B)" in texto
    tem_c = "(C)" in texto
    tem_d = "(D)" in texto

    duplicada = any(texto.count(alt) > 1 for alt in ["(A)", "(B)", "(C)", "(D)"])

    if tem_a and tem_b and tem_c and tem_d and not duplicada and len(texto) > 120:
        return "valida"

    if tem_a and tem_b and tem_c and not duplicada and len(texto) > 120:
        return "valida_parcial"

    return "revisar_manual"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

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
