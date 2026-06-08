import sqlite3
import pandas as pd

DB = "app/db/planos_aula.db"

PESOS_ENAMED = {
    "Clínica Médica": 0.30,
    "Cirurgia": 0.20,
    "Ginecologia e Obstetrícia": 0.20,
    "Pediatria": 0.15,
    "Saúde Coletiva": 0.15,
}

def calcular_balanceamento(db_path=DB):
    con = sqlite3.connect(db_path)

    df = pd.read_sql_query("""
        SELECT 
            CASE 
                WHEN area IS NULL OR TRIM(area) = '' THEN 'Não classificada'
                ELSE area 
            END AS area,
            COUNT(*) AS quantidade
        FROM questoes
        GROUP BY area
    """, con)

    con.close()

    total = int(df["quantidade"].sum())
    resultado = {}

    for area, peso_ideal in PESOS_ENAMED.items():
        atual = int(df.loc[df["area"] == area, "quantidade"].sum())
        percentual_atual = atual / total if total else 0

        if percentual_atual == 0:
            fator = 2.0
        else:
            fator = peso_ideal / percentual_atual

        fator = max(0.35, min(fator, 2.0))

        resultado[area] = {
            "quantidade": atual,
            "percentual_atual": round(percentual_atual * 100, 2),
            "percentual_ideal": round(peso_ideal * 100, 2),
            "fator_balanceamento": round(fator, 2),
            "status": "Excesso" if percentual_atual > peso_ideal else "Déficit"
        }

    return resultado

def fator_area(area):
    dados = calcular_balanceamento()
    return dados.get(area, {}).get("fator_balanceamento", 1.0)

if __name__ == "__main__":
    dados = calcular_balanceamento()
    for area, info in dados.items():
        print(area, info)
