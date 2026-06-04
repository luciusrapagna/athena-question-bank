import sqlite3

con = sqlite3.connect("app/db/planos_aula.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS importacoes_questoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo TEXT,
    total_registros INTEGER,
    importado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

con.commit()
con.close()

print("Tabela de importações criada.")
