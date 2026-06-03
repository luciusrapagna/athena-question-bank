import sqlite3

conn = sqlite3.connect("database/question_bank.db")
cur = conn.cursor()

cur.execute("""
SELECT numero_questao,
       qualidade,
       substr(texto_questao,1,1500)
FROM questoes_extraidas
WHERE qualidade <> 'valida'
LIMIT 10
""")

for numero, qualidade, texto in cur.fetchall():
    print("\n" + "="*100)
    print(f"QUESTAO {numero} | {qualidade}")
    print("="*100)
    print(texto)

conn.close()
