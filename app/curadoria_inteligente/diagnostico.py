import sqlite3
import pandas as pd
from pathlib import Path
from app.curadoria_inteligente.score_qualidade import calcular_score

DB = Path("app/db/planos_aula.db")
OUT = Path("outputs/relatorios")
OUT.mkdir(parents=True, exist_ok=True)

def carregar_questoes():
    con = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM questoes", con)
    con.close()
    return df

def executar_diagnostico():
    df = carregar_questoes()

    registros = []
    for _, row in df.iterrows():
        q = row.to_dict()
        score, status, problemas = calcular_score(q)

        registros.append({
            "id": q.get("id"),
            "fonte": q.get("fonte"),
            "ano": q.get("ano"),
            "area": q.get("area"),
            "assunto": q.get("assunto"),
            "competencia": q.get("competencia"),
            "habilidade": q.get("habilidade"),
            "score": score,
            "status": status,
            "problemas": problemas,
        })

    rel = pd.DataFrame(registros)
    arquivo = OUT / "relatorio_curadoria_inteligente.csv"
    rel.to_csv(arquivo, index=False, encoding="utf-8-sig")

    resumo = rel["status"].value_counts().to_dict()

    print("Relatório gerado em:", arquivo)
    print("Resumo:")
    print(resumo)

if __name__ == "__main__":
    executar_diagnostico()
