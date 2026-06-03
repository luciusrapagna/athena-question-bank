import sqlite3
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from app.services.identificador_prova import identificar_nome, gerar_hash
from app.repositories.provas_repository import buscar_prova_por_hash, criar_prova

DB_PATH = "app/db/planos_aula.db"


def texto_limpo(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() == "nan":
        return ""

    return texto


def importar():
    root = Tk()
    root.withdraw()

    arquivo = askopenfilename(
        title="Selecione o XLSX estruturado da prova",
        filetypes=[("Excel", "*.xlsx")]
    )

    if not arquivo:
        print("Nenhum arquivo selecionado.")
        return

    dados_prova = identificar_nome(arquivo)
    hash_arquivo = gerar_hash(arquivo)

    existente = buscar_prova_por_hash(hash_arquivo)

    if existente:
        print("Esta prova já existe no banco.")
        print("ID:", existente[0])
        print("Nome:", existente[1])
        print("Ano:", existente[2])
        print("Instituição:", existente[3])
        return

    nome = dados_prova["prova"]
    ano = dados_prova["ano"]
    instituicao = dados_prova["instituicao"]

    prova_id = criar_prova(
        nome=nome,
        ano=ano,
        instituicao=instituicao,
        hash_arquivo=hash_arquivo,
        arquivo_origem=arquivo
    )

    df = pd.read_excel(arquivo)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    total = 0

    for _, row in df.iterrows():
        enunciado = texto_limpo(row.get("enunciado", ""))

        if not enunciado:
            continue

        cur.execute("""
            INSERT INTO questoes (
                prova_id,
                enunciado,
                alternativa_a,
                alternativa_b,
                alternativa_c,
                alternativa_d,
                alternativa_e,
                prova,
                ano,
                fonte
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prova_id,
            enunciado,
            texto_limpo(row.get("alternativa_a", "")),
            texto_limpo(row.get("alternativa_b", "")),
            texto_limpo(row.get("alternativa_c", "")),
            texto_limpo(row.get("alternativa_d", "")),
            texto_limpo(row.get("alternativa_e", "")),
            nome,
            ano,
            arquivo
        ))

        total += 1

    con.commit()
    con.close()

    print(f"Prova cadastrada com ID {prova_id}.")
    print(f"{total} questões importadas.")


if __name__ == "__main__":
    importar()
