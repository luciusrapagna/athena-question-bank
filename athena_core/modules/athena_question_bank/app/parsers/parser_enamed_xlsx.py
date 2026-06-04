import re
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import pandas as pd


def selecionar_xlsx():

    root = Tk()
    root.withdraw()

    return askopenfilename(
        title="Selecione o XLSX extraído do PDF",
        filetypes=[("Excel", "*.xlsx")]
    )


def encontrar_questoes(linhas):

    indices = []

    for i, linha in enumerate(linhas):

        txt = str(linha).strip().upper()

        if re.match(r"QUESTÃO\s+\d+", txt):
            indices.append(i)

    return indices


def extrair_questao(bloco):

    numero = None

    enunciado = []

    a = b = c = d = e = ""

    alternativa_atual = None

    for linha in bloco:

        txt = str(linha).strip()

        if not txt:
            continue

        if numero is None:

            m = re.match(r"QUESTÃO\s+(\d+)", txt.upper())

            if m:
                numero = int(m.group(1))
                continue

        if re.match(r"^\(A\)", txt):
            alternativa_atual = "A"
            a = re.sub(r"^\(A\)\s*", "", txt)
            continue

        if re.match(r"^\(B\)", txt):
            alternativa_atual = "B"
            b = re.sub(r"^\(B\)\s*", "", txt)
            continue

        if re.match(r"^\(C\)", txt):
            alternativa_atual = "C"
            c = re.sub(r"^\(C\)\s*", "", txt)
            continue

        if re.match(r"^\(D\)", txt):
            alternativa_atual = "D"
            d = re.sub(r"^\(D\)\s*", "", txt)
            continue

        if re.match(r"^\(E\)", txt):
            alternativa_atual = "E"
            e = re.sub(r"^\(E\)\s*", "", txt)
            continue

        if alternativa_atual == "A":
            a += " " + txt

        elif alternativa_atual == "B":
            b += " " + txt

        elif alternativa_atual == "C":
            c += " " + txt

        elif alternativa_atual == "D":
            d += " " + txt

        elif alternativa_atual == "E":
            e += " " + txt

        else:
            enunciado.append(txt)

    return {
        "numero": numero,
        "enunciado": " ".join(enunciado),
        "alternativa_a": a.strip(),
        "alternativa_b": b.strip(),
        "alternativa_c": c.strip(),
        "alternativa_d": d.strip(),
        "alternativa_e": e.strip()
    }


def main():

    arquivo = selecionar_xlsx()

    if not arquivo:
        print("Nenhum arquivo selecionado.")
        return

    df = pd.read_excel(arquivo)

    linhas = df.iloc[:, 0].fillna("").tolist()

    indices = encontrar_questoes(linhas)

    questoes = []

    for i in range(len(indices)):

        inicio = indices[i]

        if i < len(indices) - 1:
            fim = indices[i + 1]
        else:
            fim = len(linhas)

        bloco = linhas[inicio:fim]

        questao = extrair_questao(bloco)

        if questao["numero"]:
            questoes.append(questao)

    resultado = pd.DataFrame(questoes)

    output = Path("outputs")
    output.mkdir(exist_ok=True)

    arquivo_saida = output / "questoes_enamed_estruturadas.xlsx"

    resultado.to_excel(
        arquivo_saida,
        index=False
    )

    print()
    print("Questões encontradas:", len(resultado))
    print("Arquivo:", arquivo_saida)


if __name__ == "__main__":
    main()