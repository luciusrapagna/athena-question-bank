import csv
from pathlib import Path


CAMINHO_COMPETENCIAS = Path("data/competencias/competencias.csv")


def carregar_competencias(caminho=CAMINHO_COMPETENCIAS):
    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de competências não encontrado: {caminho}")

    competencias = []

    with open(caminho, mode="r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            competencias.append({
                "codigo": linha.get("codigo", "").strip(),
                "area": linha.get("area", "").strip(),
                "competencia": linha.get("competencia", "").strip(),
                "habilidade": linha.get("habilidade", "").strip(),
            })

    return competencias


def filtrar_por_area(area):
    competencias = carregar_competencias()
    area_normalizada = area.strip().lower()

    return [
        item for item in competencias
        if item["area"].lower() == area_normalizada
    ]


def buscar_por_codigo(codigo):
    competencias = carregar_competencias()
    codigo_normalizado = codigo.strip().upper()

    for item in competencias:
        if item["codigo"].upper() == codigo_normalizado:
            return item

    return None
