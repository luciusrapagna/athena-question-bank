import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

root = Tk()
root.withdraw()

arquivo = askopenfilename(
    title="Selecione o XLSX gerado do PDF",
    filetypes=[("Excel", "*.xlsx")]
)

if not arquivo:
    print("Nenhum arquivo selecionado.")
    raise SystemExit

print(f"\nArquivo: {arquivo}\n")

df = pd.read_excel(arquivo)

print("Colunas:")
print(df.columns.tolist())

print("\nPrimeiras 150 linhas:\n")

for i in range(min(150, len(df))):
    print(f"[{i}] {df.iloc[i,0]}")
