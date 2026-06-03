import csv
import re
from app.config_paths import BANCO_QUESTOES, BANCO_PLANOS, BANCO_RELACIONAMENTOS


def normalizar(texto):
    texto = str(texto or "").lower()
    texto = re.sub(r"[^a-záéíóúâêôãõç0-9\s]", " ", texto)
    return " ".join(texto.split())


def palavras_relevantes(texto):
    stopwords = {
        "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
        "a", "o", "e", "ou", "um", "uma", "para", "por", "com", "sem",
        "que", "se", "ao", "à", "as", "os", "sobre"
    }
    return {
        p for p in normalizar(texto).split()
        if len(p) >= 4 and p not in stopwords
    }


def score_aderencia(questao, plano):
    texto_questao = " ".join([
        questao.get("area", ""),
        questao.get("assunto", ""),
        questao.get("enunciado", "")
    ])

    texto_plano = " ".join([
        plano.get("area", ""),
        plano.get("assunto", ""),
        plano.get("objetivos", ""),
        plano.get("conteudos", "")
    ])

    pq = palavras_relevantes(texto_questao)
    pp = palavras_relevantes(texto_plano)

    if not pq or not pp:
        return 0

    intersecao = pq.intersection(pp)
    score = len(intersecao) / max(len(pp), 1)

    if questao.get("area") == plano.get("area"):
        score += 0.30

    return round(score, 3)


def carregar_csv(caminho):
    with open(caminho, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def gerar_relacionamentos():
    questoes = carregar_csv(BANCO_QUESTOES)
    planos = carregar_csv(BANCO_PLANOS)

    registros = []
    contador = 1

    for questao in questoes:
        for plano in planos:
            score = score_aderencia(questao, plano)

            if score > 0:
                registros.append({
                    "id_relacao": f"REL{contador:05d}",
                    "id_questao": questao.get("id_questao", ""),
                    "id_aula": plano.get("id_aula", ""),
                    "area": questao.get("area", ""),
                    "assunto": plano.get("assunto", ""),
                    "score_aderencia": score,
                })
                contador += 1

    registros = sorted(
        registros,
        key=lambda x: float(x["score_aderencia"]),
        reverse=True
    )

    with open(BANCO_RELACIONAMENTOS, "w", encoding="utf-8-sig", newline="") as f:
        campos = ["id_relacao", "id_questao", "id_aula", "area", "assunto", "score_aderencia"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)

    print(f"Relacionamentos gerados: {len(registros)}")
    print(f"Banco gerado em: {BANCO_RELACIONAMENTOS}")


if __name__ == "__main__":
    gerar_relacionamentos()
