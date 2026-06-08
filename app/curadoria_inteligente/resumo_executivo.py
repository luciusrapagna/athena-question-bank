import pandas as pd
from pathlib import Path

REL = Path("outputs/relatorios/relatorio_curadoria_inteligente.csv")
OUT = Path("outputs/relatorios/resumo_curadoria_inteligente.csv")

def gerar_resumo():
    df = pd.read_csv(REL)

    linhas = []

    linhas.append({"indicador": "Total de questões", "quantidade": len(df)})

    for status, qtd in df["status"].value_counts().items():
        linhas.append({"indicador": f"Questões com status {status}", "quantidade": int(qtd)})

    campos = ["area", "assunto", "competencia", "habilidade"]
    for campo in campos:
        qtd = df[campo].isna().sum() + (df[campo].astype(str).str.strip() == "").sum()
        linhas.append({"indicador": f"Questões sem {campo}", "quantidade": int(qtd)})

    criticas = int((df["status"] == "Crítica").sum())
    revisar = int((df["status"] == "Revisar").sum())

    linhas.append({"indicador": "Questões que exigem revisão", "quantidade": criticas + revisar})

    resumo = pd.DataFrame(linhas)
    resumo.to_csv(OUT, index=False, encoding="utf-8-sig")

    print("Resumo executivo gerado em:", OUT)
    print(resumo)

if __name__ == "__main__":
    gerar_resumo()
