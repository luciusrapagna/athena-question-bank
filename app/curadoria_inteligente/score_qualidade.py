def vazio(valor):
    texto = str(valor or "").strip()
    return texto == "" or texto.lower() in ["nan", "none", "null"]

def tem_alternativas(q):
    grupos = [
        ["alternativas"],
        ["alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d"],
        ["a", "b", "c", "d"],
        ["opcao_a", "opcao_b", "opcao_c", "opcao_d"],
    ]

    for grupo in grupos:
        presentes = 0
        for campo in grupo:
            if campo in q and not vazio(q.get(campo)):
                presentes += 1
        if presentes >= 4:
            return True

    texto = str(q.get("enunciado", "") or "")
    marcadores = ["A)", "B)", "C)", "D)", "A.", "B.", "C.", "D."]
    return sum(1 for m in marcadores if m in texto) >= 4

def calcular_score(q):
    score = 100
    problemas = []

    campos_obrigatorios = {
        "enunciado": 25,
        "area": 15,
        "assunto": 15,
        "competencia": 15,
        "habilidade": 15,
    }

    for campo, peso in campos_obrigatorios.items():
        if vazio(q.get(campo)):
            score -= peso
            problemas.append(f"Sem {campo}")

    if not tem_alternativas(q):
        score -= 15
        problemas.append("Sem alternativas")

    enunciado = str(q.get("enunciado", "") or "")
    if len(enunciado.strip()) < 40:
        score -= 10
        problemas.append("Enunciado muito curto")

    if "nan" in enunciado.lower():
        score -= 10
        problemas.append("Ruído nan no enunciado")

    score = max(score, 0)

    if score >= 90:
        status = "Excelente"
    elif score >= 70:
        status = "Boa"
    elif score >= 50:
        status = "Revisar"
    else:
        status = "Crítica"

    return score, status, "; ".join(problemas)
