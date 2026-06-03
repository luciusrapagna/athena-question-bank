import sqlite3

conn = sqlite3.connect("database/question_bank.db")
cur = conn.cursor()

cur.execute("""
SELECT numero_questao,
       substr(texto_questao,1,1200)
FROM questoes_extraidas
WHERE qualidade='revisar_manual'
LIMIT 10
""")

for numero, texto in cur.fetchall():
    print("\n" + "="*80)
    print(f"QUESTAO {numero}")
    print("="*80)
    print(texto)

conn.close()
