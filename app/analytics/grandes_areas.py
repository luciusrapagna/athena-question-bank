import sqlite3
import pandas as pd

DB_PATH = "app/db/planos_aula.db"

con = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    """
    SELECT grande_area
    FROM questoes
    WHERE grande_area IS NOT NULL
    """,
    con
)

con.close()

if len(df) == 0:
    print("Nenhuma questão classificada.")
    raise SystemExit

resumo = (
    df["grande_area"]
    .value_counts()
    .reset_index()
)

resumo.columns = [
    "Grande Área",
    "Frequência"
]

resumo["Percentual"] = (
    resumo["Frequência"]
    / resumo["Frequência"].sum()
    * 100
).round(2)

print(resumo)

resumo.to_excel(
    "outputs/analytics_grandes_areas.xlsx",
    index=False
)

print()
print("Arquivo gerado:")
print("outputs/analytics_grandes_areas.xlsx")
