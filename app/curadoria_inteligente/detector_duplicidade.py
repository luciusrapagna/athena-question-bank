import sqlite3
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz

DB = Path("app/db/planos_aula.db")
OUT = Path("outputs/relatorios")
OUT.mkdir(parents=True, exist_ok=True)

def limpar(texto):
    return " ".join(str(texto or "").lower().split())

def carregar():
    con = sqlite3.connect(DB)
    df = pd.read_sql_query("""
        SELECT id, fonte, ano, area, assunto, enunciado
        FROM questoes
        WHERE enunciado IS NOT NULL
    """, con)
    con.close()
    df["texto_limpo"] = df["enunciado"].apply(limpar)
    df = df[df["texto_limpo"].str.len() > 40].copy()
    return df

def detectar(limite=94):
    df = carregar()
    registros = []

    grupos = df.groupby(["area", "assunto"], dropna=False)

    for (area, assunto), grupo in grupos:
        dados = grupo.to_dict("records")

        if len(dados) < 2:
            continue

        for i in range(len(dados)):
            q1 = dados[i]

            for j in range(i + 1, len(dados)):
                q2 = dados[j]

                score = fuzz.token_set_ratio(q1["texto_limpo"], q2["texto_limpo"])

                if score >= limite:
                    registros.append({
                        "id_1": q1["id"],
                        "fonte_1": q1["fonte"],
                        "ano_1": q1["ano"],
                        "area_1": q1["area"],
                        "assunto_1": q1["assunto"],
                        "id_2": q2["id"],
                        "fonte_2": q2["fonte"],
                        "ano_2": q2["ano"],
                        "area_2": q2["area"],
                        "assunto_2": q2["assunto"],
                        "similaridade": round(score, 2),
                        "trecho_1": q1["enunciado"][:250],
                        "trecho_2": q2["enunciado"][:250],
                    })

    rel = pd.DataFrame(registros)
    arquivo = OUT / "relatorio_duplicidades_inteligente.csv"
    rel.to_csv(arquivo, index=False, encoding="utf-8-sig")

    print("Relatório gerado em:", arquivo)
    print("Possíveis duplicidades:", len(rel))

    if len(rel) > 0:
        print(rel[["id_1", "id_2", "similaridade", "assunto_1", "assunto_2"]].head(20))

if __name__ == "__main__":
    detectar()
