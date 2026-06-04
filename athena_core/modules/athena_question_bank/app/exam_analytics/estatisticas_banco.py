from pathlib import Path
import pandas as pd
from app.config_paths import BANCO_QUESTOES

BASE_DIR = Path(__file__).resolve().parents[2]
DIR_RELATORIOS = BASE_DIR / "outputs" / "relatorios"
DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)

SAIDA_AREAS = DIR_RELATORIOS / "percentual_5_grandes_areas.csv"
SAIDA_ASSUNTOS_POR_AREA = DIR_RELATORIOS / "percentual_assuntos_por_area.csv"
SAIDA_BLUEPRINT = DIR_RELATORIOS / "blueprint_exam_analytics.csv"


GRANDES_AREAS = [
    "Clínica Médica",
    "Cirurgia",
    "Pediatria",
    "Ginecologia e Obstetrícia",
    "Saúde Coletiva",
]


def carregar_banco():
    if not BANCO_QUESTOES.exists():
        print("Banco de questões ainda não encontrado.")
        return pd.DataFrame()

    return pd.read_csv(BANCO_QUESTOES, encoding="utf-8-sig")


def gerar_percentual_areas(df):
    total = len(df)

    dados = []

    for area in GRANDES_AREAS:
        n = len(df[df["area"] == area])
        percentual = round((n / total) * 100, 2) if total else 0

        dados.append({
            "grande_area": area,
            "n_questoes": n,
            "percentual_total_prova": percentual,
        })

    return pd.DataFrame(dados)


def gerar_percentual_assuntos_por_area(df):
    registros = []

    for area in GRANDES_AREAS:
        df_area = df[df["area"] == area]
        total_area = len(df_area)

        if total_area == 0:
            continue

        contagem = (
            df_area["assunto"]
            .fillna("Assunto não informado")
            .value_counts()
            .reset_index()
        )

        contagem.columns = ["assunto", "n_questoes"]

        for _, linha in contagem.iterrows():
            registros.append({
                "grande_area": area,
                "assunto": linha["assunto"],
                "n_questoes": int(linha["n_questoes"]),
                "percentual_dentro_area": round((linha["n_questoes"] / total_area) * 100, 2),
                "total_questoes_area": total_area,
            })

    return pd.DataFrame(registros)


def gerar_blueprint(df):
    areas = gerar_percentual_areas(df)
    assuntos = gerar_percentual_assuntos_por_area(df)

    blueprint = assuntos.merge(
        areas[["grande_area", "percentual_total_prova"]],
        on="grande_area",
        how="left"
    )

    return blueprint


def gerar_estatisticas():
    df = carregar_banco()

    if df.empty:
        return None

    areas = gerar_percentual_areas(df)
    assuntos = gerar_percentual_assuntos_por_area(df)
    blueprint = gerar_blueprint(df)

    areas.to_csv(SAIDA_AREAS, index=False, encoding="utf-8-sig")
    assuntos.to_csv(SAIDA_ASSUNTOS_POR_AREA, index=False, encoding="utf-8-sig")
    blueprint.to_csv(SAIDA_BLUEPRINT, index=False, encoding="utf-8-sig")

    print("EXAM ANALYTICS gerado com sucesso.")
    print(f"Percentual das 5 grandes áreas: {SAIDA_AREAS}")
    print(f"Percentual dos assuntos por área: {SAIDA_ASSUNTOS_POR_AREA}")
    print(f"Blueprint completo: {SAIDA_BLUEPRINT}")

    return {
        "areas": areas,
        "assuntos_por_area": assuntos,
        "blueprint": blueprint,
    }


if __name__ == "__main__":
    gerar_estatisticas()
