import csv
from collections import Counter
from app.config_paths import BANCO_QUESTOES, DIR_RELATORIOS


def carregar_questoes():
    with open(BANCO_QUESTOES, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def gerar_estatisticas():
    questoes = carregar_questoes()
    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)

    total = len(questoes)

    por_area = Counter(q.get("area", "Não classificada") for q in questoes)
    por_fonte = Counter(q.get("fonte", "Não identificada") for q in questoes)
    por_prova = Counter(q.get("prova", "Não identificada") for q in questoes)

    caminho = DIR_RELATORIOS / "estatisticas_banco_questoes.csv"

    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["categoria", "item", "n_questoes", "percentual"])

        for area, n in por_area.items():
            writer.writerow(["area", area, n, round((n / total) * 100, 2) if total else 0])

        for fonte, n in por_fonte.items():
            writer.writerow(["fonte", fonte, n, round((n / total) * 100, 2) if total else 0])

        for prova, n in por_prova.items():
            writer.writerow(["prova", prova, n, round((n / total) * 100, 2) if total else 0])

    print(f"Total de questões: {total}")
    print(f"Relatório salvo em: {caminho}")


if __name__ == "__main__":
    gerar_estatisticas()
