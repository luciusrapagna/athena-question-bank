import sqlite3
import pandas as pd
from pathlib import Path

DB = "app/db/planos_aula.db"
OUT = Path("outputs/relatorios")
OUT.mkdir(parents=True, exist_ok=True)

def classificar_status(qtd):
    if qtd >= 50:
        return "Forte"
    elif qtd >= 20:
        return "Médio"
    elif qtd >= 5:
        return "Fraco"
    else:
        return "Crítico"

def gerar_auditoria_assuntos():
    con = sqlite3.connect(DB)

    df = pd.read_sql_query("""
        SELECT
            CASE 
                WHEN grande_area IS NULL OR TRIM(grande_area) = '' THEN 'Não classificada'
                ELSE grande_area
            END AS area,
            CASE
                WHEN assunto IS NOT NULL AND TRIM(assunto) <> '' THEN assunto
                WHEN tema_indexado IS NOT NULL AND TRIM(tema_indexado) <> '' THEN tema_indexado
                WHEN tema IS NOT NULL AND TRIM(tema) <> '' THEN tema
                ELSE 'Sem assunto definido'
            END AS assunto,
            COUNT(*) AS quantidade
        FROM questoes
        GROUP BY area, assunto
        ORDER BY area, quantidade DESC
    """, con)

    con.close()

    totais = df.groupby("area")["quantidade"].sum().to_dict()

    df["percentual_na_area"] = df.apply(
        lambda r: round((r["quantidade"] / totais.get(r["area"], 1)) * 100, 2),
        axis=1
    )

    df["status"] = df["quantidade"].apply(classificar_status)

    csv_path = OUT / "auditoria_enamed_por_assunto.csv"
    md_path = OUT / "relatorio_executivo_auditoria_assuntos.md"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Relatório Executivo – Auditoria ENAMED por Assunto\n\n")
        f.write("Este relatório identifica a distribuição de questões por assunto dentro de cada grande área.\n\n")

        for area in sorted(df["area"].unique()):
            sub = df[df["area"] == area].copy()
            total_area = int(sub["quantidade"].sum())

            f.write(f"## {area}\n\n")
            f.write(f"Total de questões na área: **{total_area}**\n\n")

            criticos = sub[sub["status"] == "Crítico"]
            fracos = sub[sub["status"] == "Fraco"]
            fortes = sub[sub["status"] == "Forte"]

            f.write("### Assuntos mais frequentes\n\n")
            for _, r in sub.head(10).iterrows():
                f.write(f"- {r['assunto']}: {r['quantidade']} questões ({r['percentual_na_area']}%) — {r['status']}\n")

            f.write("\n### Pontos de atenção\n\n")
            if not criticos.empty:
                f.write("Assuntos críticos:\n")
                for _, r in criticos.head(15).iterrows():
                    f.write(f"- {r['assunto']}: {r['quantidade']} questão(ões)\n")
            elif not fracos.empty:
                f.write("Assuntos fracos:\n")
                for _, r in fracos.head(15).iterrows():
                    f.write(f"- {r['assunto']}: {r['quantidade']} questões\n")
            else:
                f.write("Não foram identificados assuntos críticos entre os principais agrupamentos.\n")

            f.write("\n")

    print("Auditoria ENAMED por assunto concluída.")
    print(f"CSV: {csv_path}")
    print(f"Relatório: {md_path}")
    print()
    print(df.head(40).to_string(index=False))

if __name__ == "__main__":
    gerar_auditoria_assuntos()
