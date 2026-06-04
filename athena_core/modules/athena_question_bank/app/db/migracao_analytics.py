import sqlite3

con = sqlite3.connect("app/db/planos_aula.db")
cur = con.cursor()

try:
    cur.execute("ALTER TABLE questoes ADD COLUMN grande_area TEXT")
except:
    pass

try:
    cur.execute("ALTER TABLE questoes ADD COLUMN subarea TEXT")
except:
    pass

try:
    cur.execute("ALTER TABLE questoes ADD COLUMN competencia TEXT")
except:
    pass

try:
    cur.execute("ALTER TABLE questoes ADD COLUMN habilidade TEXT")
except:
    pass

con.commit()
con.close()

print("Estrutura atualizada.")
