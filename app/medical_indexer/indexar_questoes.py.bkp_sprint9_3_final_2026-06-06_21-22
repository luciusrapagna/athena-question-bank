import sqlite3
import re
from pathlib import Path

DB = "app/db/planos_aula.db"

FALLBACK = "Tema médico não classificado"

DICIONARIO_LOCAL = {
    "Clínica Médica": {
        "Cardiologia": {
            "Hipertensão arterial": ["hipertensão", "pressão arterial", "anti-hipertensivo", "crise hipertensiva"],
            "Insuficiência cardíaca": ["dispneia", "edema", "fração de ejeção", "insuficiência cardíaca"],
            "Síndrome coronariana": ["dor torácica", "infarto", "iam", "angina", "troponina"],
        },
        "Endocrinologia": {
            "Diabetes mellitus": ["diabetes", "glicemia", "insulina", "hipoglicemia", "cetoacidose"],
            "Tireoide": ["tsh", "t4", "hipotireoidismo", "hipertireoidismo"],
        },
        "Infectologia": {
            "Sepse": ["sepse", "choque séptico", "lactato", "antibiótico"],
            "Tuberculose": ["tuberculose", "baciloscopia", "rifampicina", "isoniazida"],
            "HIV": ["hiv", "aids", "antirretroviral", "cd4"],
        },
    },
    "Cirurgia": {
        "Cirurgia Geral": {
            "Abdome agudo": ["abdome agudo", "apendicite", "peritonite", "obstrução intestinal"],
            "Trauma": ["trauma", "atls", "hemorragia", "fratura", "politrauma"],
        },
        "Urologia": {
            "Litíase urinária": ["cálculo ureteral", "litíase", "cólica renal", "duplo j"],
        },
    },
    "Pediatria": {
        "Neonatologia": {
            "Reanimação neonatal": ["apgar", "recém-nascido", "reanimação neonatal", "prematuro"],
        },
        "Pediatria Geral": {
            "Crescimento e desenvolvimento": ["crescimento", "desenvolvimento neuropsicomotor", "percentil"],
            "Vacinação infantil": ["vacina", "calendário vacinal", "imunização"],
        },
    },
    "Ginecologia e Obstetrícia": {
        "Obstetrícia": {
            "Pré-natal": ["pré-natal", "gestante", "idade gestacional", "parto"],
            "Síndromes hipertensivas da gestação": ["pré-eclâmpsia", "eclâmpsia", "hipertensão gestacional"],
        },
        "Ginecologia": {
            "Rastreamento do câncer de colo": ["papanicolau", "hpv", "colo uterino", "citologia"],
            "Endometriose": ["endometriose", "dor pélvica", "dismenorreia"],
        },
    },
    "Saúde Coletiva": {
        "Epidemiologia": {
            "Indicadores de saúde": ["incidência", "prevalência", "mortalidade", "letalidade"],
            "Vigilância em saúde": ["notificação", "vigilância epidemiológica", "surto"],
        },
        "Atenção Primária": {
            "Estratégia Saúde da Família": ["atenção primária", "esf", "territorialização", "adscrição"],
            "SUS": ["sus", "universalidade", "equidade", "integralidade"],
        },
    },
}

COMPETENCIAS = {
    "Clínica Médica": "Cuidado integral do adulto e raciocínio clínico",
    "Cirurgia": "Avaliação, decisão e manejo de condições cirúrgicas",
    "Pediatria": "Atenção integral à saúde da criança e do adolescente",
    "Ginecologia e Obstetrícia": "Atenção integral à saúde da mulher, gestação e parto",
    "Saúde Coletiva": "Atenção primária, vigilância, SUS e saúde coletiva",
}

def normalizar(txt):
    if not txt:
        return ""
    return re.sub(r"\s+", " ", str(txt).lower()).strip()

def classificar_local(texto):
    texto_n = normalizar(texto)
    melhor = None

    for area, especialidades in DICIONARIO_LOCAL.items():
        for especialidade, temas in especialidades.items():
            for tema, palavras in temas.items():
                pontos = sum(1 for p in palavras if p.lower() in texto_n)
                if pontos > 0:
                    score = min(0.95, 0.55 + pontos * 0.1)
                    candidato = {
                        "tema": tema,
                        "subtema": tema,
                        "especialidade": especialidade,
                        "area": area,
                        "competencia": COMPETENCIAS.get(area, ""),
                        "confianca": score,
                    }
                    if melhor is None or candidato["confianca"] > melhor["confianca"]:
                        melhor = candidato

    return melhor

def classificar_api_medica(texto):
    """
    Camada reservada para API médica já integrada.
    Mantida segura: se a API falhar, o fluxo local permanece funcionando.
    """
    try:
        from app.services.medical_api import classificar_texto_medico

        r = classificar_texto_medico(texto)

        if not r:
            return None

        return {
            "tema": r.get("tema_principal") or r.get("tema") or FALLBACK,
            "subtema": r.get("subtema") or r.get("tema_principal") or FALLBACK,
            "especialidade": r.get("especialidade") or "",
            "area": r.get("area") or "",
            "competencia": r.get("competencia_enamed") or "",
            "confianca": float(r.get("confianca", 0.75)),
        }

    except Exception:
        return None

def decidir_classificacao(texto):
    local = classificar_local(texto)

    if local and local["confianca"] >= 0.75:
        return local

    api = classificar_api_medica(texto)

    if api and api.get("tema") and api["tema"] != FALLBACK:
        if local:
            api["confianca"] = max(api.get("confianca", 0.75), local["confianca"])
        return api

    if local:
        return local

    return {
        "tema": FALLBACK,
        "subtema": FALLBACK,
        "especialidade": FALLBACK,
        "area": "",
        "competencia": "",
        "confianca": 0.1,
    }

def texto_questao(row):
    partes = [
        row.get("enunciado"),
        row.get("texto"),
        row.get("alternativa_a"),
        row.get("alternativa_b"),
        row.get("alternativa_c"),
        row.get("alternativa_d"),
        row.get("alternativa_e"),
        row.get("assunto"),
    ]
    return " ".join([str(p) for p in partes if p])

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM questoes")
    questoes = cur.fetchall()

    total = 0

    for q in questoes:
        d = dict(q)
        texto = texto_questao(d)
        c = decidir_classificacao(texto)

        tema = c["tema"] or d.get("assunto") or c["subtema"] or c["especialidade"] or FALLBACK
        if tema == "Assunto não identificado":
            tema = FALLBACK

        cur.execute("""
            UPDATE questoes
            SET tema_indexado = ?,
                assunto = COALESCE(NULLIF(assunto, ''), ?),
                subtema_indexado = ?,
                especialidade = ?,
                competencia_enamed = ?,
                confianca_indexacao = ?
            WHERE id = ?
        """, (
            tema,
            tema,
            c["subtema"] or tema,
            c["especialidade"] or FALLBACK,
            c["competencia"] or "",
            c["confianca"],
            d["id"]
        ))

        total += 1

    con.commit()
    con.close()
    print(f"Indexação médica inteligente concluída: {total} questões processadas.")

if __name__ == "__main__":
    main()
