from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

BANCO_QUESTOES = BASE_DIR / "data" / "banco_questoes" / "banco_questoes.csv"
SAIDA = BASE_DIR / "data" / "banco_questoes" / "estatisticas_banco.csv"


def gerar_estatisticas():

    if not BANCO_QUESTOES.exists():
        print("Banco de questões ainda não encontrado.")
        return None

    df = pd.read_csv(
        BANCO_QUESTOES,
        sep=";",
        encoding="utf-8"
    )

    estatisticas = {
        "total_questoes": [len(df)]
    }

    if "grande_area" in df.columns:
        estatisticas["areas_identificadas"] = [
            df["grande_area"].nunique()
        ]

    if "assunto" in df.columns:
        estatisticas["assuntos_identificados"] = [
            df["assunto"].nunique()
        ]

    pd.DataFrame(estatisticas).to_csv(
        SAIDA,
        sep=";",
        index=False,
        encoding="utf-8"
    )

    print("Estatísticas geradas com sucesso.")
