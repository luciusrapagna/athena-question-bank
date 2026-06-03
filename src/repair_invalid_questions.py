import re
import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def limpar_linhas(texto):
    texto = texto or ""
    texto = texto.replace("\uFFFE", "")
    texto = texto.replace("￾", "-")
    texto = texto.replace("\r", "")

    linhas = []
    for linha in texto.splitlines():
        l = linha.strip()
        if not l:
            continue
        if "Núcleo Mineiro" in l:
            continue
        if "Teste de Progresso" in l:
            continue
        if re.match(r"^\d+\s*$", l):
            continue
        linhas.append(l)

    return "\n".join(linhas).strip()

def pos_alt(texto, alt):
    return [m.start() for m in re.finditer(re.escape(alt), texto)]

def tentar_recortar_primeiro_abcd(texto):
    a = pos_alt(texto, "(A)")
    b = pos_alt(texto, "(B)")
    c = pos_alt(texto, "(C)")
    d = pos_alt(texto, "(D)")

    if not a or not b or not c or not d:
        return texto

    inicio_a = a[0]

    candidatos = []
    for pb in b:
        if pb > inicio_a:
            for pc in c:
                if pc > pb:
                    for pd in d:
                        if pd > pc:
                            candidatos.append((inicio_a, pb, pc, pd))
                            break
                    break
            break

    if not candidatos:
        return texto

    _, pb, pc, pd = candidatos[0]

    proximas_marcas = []
    for marca in ["(A)", "(B)", "(C)", "(D)", "QUESTÃO", "Questão"]:
        for p in pos_alt(texto[pd + 3:], marca):
            proximas_marcas.append(pd + 3 + p)

    if proximas_marcas:
        fim = min(proximas_marcas)
        texto = texto[:fim].strip()

    return texto

def validar_final(texto):
    contagens = {
        "A": texto.count("(A)"),
        "B": texto.count("(B)"),
        "C": texto.count("(C)"),
        "D": texto.count("(D)")
    }

    if contagens == {"A": 1, "B": 1, "C": 1, "D": 1} and len(texto) > 120:
        return "corrigida"

    return "revisar_manual"

def reparar(texto):
    texto = limpar_linhas(texto)
    texto = tentar_recortar_primeiro_abcd(texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    qualidade = validar_final(texto)
    return texto, qualidade

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
SELECT id, texto_questao
FROM questoes_extraidas
WHERE qualidade = 'revisar_manual'
   OR qualidade = 'revisar'
   OR qualidade IS NULL
""")

questoes = cur.fetchall()

corrigidas = 0
mantidas = 0

for qid, texto in questoes:
    novo_texto, qualidade = reparar(texto)

    cur.execute("""
    UPDATE questoes_extraidas
    SET texto_questao = ?, qualidade = ?
    WHERE id = ?
    """, (novo_texto, qualidade, qid))

    if qualidade == "corrigida":
        corrigidas += 1
    else:
        mantidas += 1

conn.commit()

cur.execute("SELECT qualidade, COUNT(*) FROM questoes_extraidas GROUP BY qualidade")
resumo = cur.fetchall()

conn.close()

print("Reparo avançado concluído.")
print(f"Corrigidas automaticamente: {corrigidas}")
print(f"Ainda precisam de revisão manual: {mantidas}")
print("Resumo:")
print(resumo)
