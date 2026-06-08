import pandas as pd
from pathlib import Path

ARQ = Path("outputs/relatorios/relatorio_duplicidades_inteligente.csv")
OUT = Path("outputs/relatorios/resumo_duplicidades_inteligente.csv")

df = pd.read_csv(ARQ)

def classe(x):
    if x >= 100:
        return "Duplicidade forte"
    elif x >= 97:
        return "Duplicidade provável"
    else:
        return "Duplicidade fraca"

df["classe"] = df["similaridade"].apply(classe)

resumo = df["classe"].value_counts().reset_index()
resumo.columns = ["classe", "quantidade"]

resumo.to_csv(OUT, index=False, encoding="utf-8-sig")

print(resumo)

print("\nTop 20 duplicidades fortes:")
print(
    df[df["classe"] == "Duplicidade forte"]
    [["id_1", "id_2", "similaridade", "area_1", "assunto_1"]]
    .head(20)
)
