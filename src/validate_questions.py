import re
import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def validar(texto):
    texto = texto or ""

    tem_a = "(A)" in texto
    tem_b = "(B)" in texto
    tem_c = "(C)" in texto
    tem_d = "(D)" in texto

    alternativas_ok = tem_a and tem_b and tem_c and tem_d

    a_duplicado = texto.count("(A)") > 1
    b_duplicado = texto.count("(B)") > 1
    c_duplicado = texto.count("(C)") > 1
    d_duplicado = texto.count("(D)") > 1

    duplicada = a_duplicado or b_duplicado or c_duplicado or d_duplicado

    cabecalho_pdf = "Núcleo Mineiro" in texto or "Teste de Progresso" in texto

    if alternativas_ok and not duplicada and not cabecalho_pdf:
        return "valida"

    return "revisar"

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
