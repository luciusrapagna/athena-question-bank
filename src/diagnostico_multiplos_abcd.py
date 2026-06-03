import sqlite3

conn = sqlite3.connect("database/question_bank.db")
cur = conn.cursor()

cur.execute("""
SELECT numero_questao, texto_questao
FROM questoes_extraidas
""")

problemas = 0

for numero, texto in cur.fetchall():

    if texto.count("(A)") > 1:
        problemas += 1
        print(f"Questão {numero}: {texto.count('(A)')} blocos A")

print()
print("Questões com múltiplos conjuntos de alternativas:", problemas)

conn.close()
