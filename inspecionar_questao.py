import pandas as pd

df = pd.read_excel("outputs/2025_caderno_1_preliminar (1)(1).xlsx")

for i, linha in enumerate(df["texto"]):

    txt = str(linha)

    if "QUESTÃO" in txt.upper():
        print(f"Linha {i}: {txt}")

        for j in range(i, min(i+8, len(df))):
            print(df.iloc[j]["texto"])

        print("="*80)
        break
