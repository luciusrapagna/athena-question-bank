import sqlite3
import pandas as pd
from pathlib import Path

DB = "app/db/planos_aula.db"
OUT = Path("outputs/relatorios")
OUT.mkdir(parents=True, exist_ok=True)

PESOS_ENAMED = {
    "Clínica Médica": 0.30,
    "Cirurgia": 0.20,
    "Ginecologia e Obstetrícia": 0.20,
    "Pediatria": 0.15,
    "Saúde Coletiva": 0.15,
}

def gerar_auditoria():
    con = sqlite3.connect(DB)

    df = pd.read_sql_query("""
        SELECT 
            CASE 
                WHEN area IS NULL OR TRIM(area) = '' THEN 'Não classificada'
                ELSE area 
            END AS area,
            COUNT(*) AS quantidade
        FROM questoes
        GROUP BY area
        ORDER BY quantidade DESC
    """, con)

    total = int(df["quantidade"].sum())

    linhas = []
    for area, peso in PESOS_ENAMED.items():
        atual = int(df.loc[df["area"] == area, "quantidade"].sum())
        ideal = round(total * peso)
        diferenca = atual - ideal

        if diferenca > 0:
            status = "Excesso"
        elif diferenca < 0:
            status = "Déficit"
        else:
            status = "Equilibrado"

        linhas.append({
            "area": area,
            "quantidade_atual": atual,
            "percentual_atual": round((atual / total) * 100, 2),
            "percentual_ideal_enamed": round(peso * 100, 2),
            "quantidade_ideal": ideal,
            "diferenca": diferenca,
            "status": status
        })

    auditoria = pd.DataFrame(linhas)

    nao_classificadas = int(df.loc[df["area"] == "Não classificada", "quantidade"].sum())

    auditoria.to_csv(OUT / "auditoria_enamed_balanceamento.csv", index=False)

    with open(OUT / "relatorio_executivo_auditoria_enamed.md", "w", encoding="utf-8") as f:
        f.write("# Relatório Executivo – Auditoria ENAMED e Balanceamento do Banco\n\n")
        f.write(f"Total de questões auditadas: **{total}**\n\n")
        f.write(f"Questões não classificadas: **{nao_classificadas}**\n\n")
        f.write("## Distribuição por área\n\n")
        f.write(auditoria.to_string(index=False))
        f.write("\n\n## Interpretação executiva\n\n")

        for _, r in auditoria.iterrows():
            f.write(
                f"- **{r['area']}**: {r['percentual_atual']}% do banco; "
                f"ideal ENAMED estimado: {r['percentual_ideal_enamed']}%; "
                f"{r['status'].lower()} de {abs(int(r['diferenca']))} questões.\n"
            )

        f.write("\n## Recomendação\n\n")
        f.write(
            "Priorizar importação, classificação e curadoria das áreas deficitárias. "
            "Durante a geração de simulados e seleção por aula, aplicar fator de correção "
            "para reduzir a dominância de áreas em excesso e favorecer áreas sub-representadas.\n"
        )

    print("Auditoria ENAMED concluída.")
    print(auditoria.to_string(index=False))
    print(f"\nArquivos gerados em: {OUT}")

if __name__ == "__main__":
    gerar_auditoria()
