import sqlite3

con = sqlite3.connect("app/db/planos_aula.db")

try:
    con.execute(
        "ALTER TABLE questoes ADD COLUMN prova_id INTEGER"
    )
    print("Coluna prova_id criada.")
except:
    print("Coluna prova_id já existe.")

con.commit()
con.close()
