import re
import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def qualidade(texto):
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

def cortar_no_proximo_numero(texto, numero_atual):
    padrao = re.compile(
        rf"\n\s*(?:QUESTÃO\s*)?({numero_atual + 1}|{numero_atual + 2})[\.\)]\s+",
        re.I
    )

    m = padrao.search(texto)

    if m:
        return texto[:m.start()].strip()

    return texto.strip()

def cortar_segundo_bloco_abcd(texto):
    pos_a = [m.start() for m in re.finditer(r"\(A\)", texto)]

    if len(pos_a) <= 1:
        return texto.strip()

    # mantém apenas até antes do segundo (A)
    return texto[:pos_a[1]].strip()

def reparar_texto(numero, texto):
    original = texto

    texto = cortar_no_proximo_numero(texto, numero)
    texto = cortar_segundo_bloco_abcd(texto)

    if len(texto) < 80:
        return original, qualidade(original)

    return texto, qualidade(texto)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
SELECT id, numero_questao, texto_questao
FROM questoes_extraidas
WHERE qualidade='revisar_manual'
""")

rows = cur.fetchall()

corrigidas = 0
parciais = 0
mantidas = 0

for qid, numero, texto in rows:
    novo_texto, nova_qualidade = reparar_texto(int(numero), texto)

    cur.execute("""
    UPDATE questoes_extraidas
    SET texto_questao=?, qualidade=?
    WHERE id=?
    """, (novo_texto, nova_qualidade, qid))

    if nova_qualidade == "valida":
        corrigidas += 1
    elif nova_qualidade == "valida_parcial":
        parciais += 1
    else:
        mantidas += 1

conn.commit()

cur.execute("SELECT qualidade, COUNT(*) FROM questoes_extraidas GROUP BY qualidade")
resumo = cur.fetchall()

conn.close()

print("ATHENA SPLITTER concluído.")
print(f"Corrigidas para válidas: {corrigidas}")
print(f"Corrigidas para válidas parciais: {parciais}")
print(f"Ainda revisar manual: {mantidas}")
print("Resumo:")
print(resumo)
