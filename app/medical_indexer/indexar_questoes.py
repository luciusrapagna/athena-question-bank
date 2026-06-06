import sqlite3
import re

DB = "app/db/planos_aula.db"
FALLBACK = "Tema médico não classificado"

HABILIDADE_PADRAO = "Interpretar dados clínicos, reconhecer hipóteses diagnósticas e selecionar condutas."

DICIONARIO = {
    "Clínica Médica": {
        "Reumatologia": {
            "Lúpus eritematoso sistêmico": ["fator antinuclear", "fan", "poliartralgia", "hidroxicloroquina", "linfopenia", "lúpus"],
        },
        "Neurologia": {
            "Doença de Parkinson": ["parkinson", "rigidez em roda dentada", "tremor de repouso", "bradicinesia"],
            "Acidente vascular cerebral": ["avc", "acidente vascular cerebral", "hemiparesia", "afasia"],
        },
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
            "Pré-natal": ["pré-natal", "gestante", "idade gestacional", "parto", "ganho de peso", "imc"],
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
            "Estratégia Saúde da Família": ["atenção primária", "aps", "esf", "territorialização", "adscrição", "rede de atenção"],
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
    return re.sub(r"\s+", " ", str(txt or "").lower()).strip()

def texto_questao(row):
    return " ".join(str(row.get(c) or "") for c in [
        "grande_area", "area", "tema", "assunto", "tema_indexado",
        "enunciado", "alternativa_a", "alternativa_b", "alternativa_c",
        "alternativa_d", "alternativa_e"
    ])

def classificar(texto, area_original=""):
    texto_n = normalizar(texto)
    melhor = None

    for area, especialidades in DICIONARIO.items():
        for especialidade, temas in especialidades.items():
            for tema, palavras in temas.items():
                pontos = sum(1 for p in palavras if p.lower() in texto_n)
                if pontos:
                    bonus_area = 1 if area_original and area_original == area else 0
                    score = pontos + bonus_area
                    cand = {
                        "area": area,
                        "especialidade": especialidade,
                        "tema": tema,
                        "competencia": COMPETENCIAS.get(area, ""),
                        "habilidade": HABILIDADE_PADRAO,
                        "score": score,
                    }
                    if melhor is None or cand["score"] > melhor["score"]:
                        melhor = cand

    if melhor:
        return melhor

    area = area_original if area_original in COMPETENCIAS else ""
    if area:
        return {
            "area": area,
            "especialidade": area,
            "tema": "Tema geral de " + area,
            "competencia": COMPETENCIAS.get(area, ""),
            "habilidade": HABILIDADE_PADRAO,
            "score": 0.2,
        }

    return {
        "area": "",
        "especialidade": "",
        "tema": FALLBACK,
        "competencia": "",
        "habilidade": "",
        "score": 0,
    }

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("""
        SELECT *
        FROM questoes
        WHERE competencia_enamed IS NULL
           OR TRIM(competencia_enamed) = ''
           OR habilidade_enamed IS NULL
           OR TRIM(habilidade_enamed) = ''
           OR tema_indexado IS NULL
           OR TRIM(tema_indexado) = ''
           OR tema_indexado = ?
    """, (FALLBACK,))

    questoes = cur.fetchall()
    total = 0

    for q in questoes:
        d = dict(q)
        texto = texto_questao(d)
        area_original = d.get("grande_area") or d.get("area") or ""
        c = classificar(texto, area_original)

        cur.execute("""
            UPDATE questoes
            SET tema_indexado = COALESCE(NULLIF(?, ''), tema_indexado),
                assunto = COALESCE(NULLIF(assunto, ''), NULLIF(?, '')),
                especialidade = COALESCE(NULLIF(?, ''), especialidade),
                subtema_indexado = COALESCE(NULLIF(?, ''), subtema_indexado),
                competencia_enamed = COALESCE(NULLIF(?, ''), competencia_enamed),
                habilidade_enamed = COALESCE(NULLIF(?, ''), habilidade_enamed),
                confianca_indexacao = ?
            WHERE id = ?
        """, (
            c["tema"],
            c["tema"],
            c["especialidade"],
            c["tema"],
            c["competencia"],
            c["habilidade"],
            c["score"],
            d["id"],
        ))
        total += 1

    con.commit()
    con.close()
    print(f"Reindexação incremental concluída: {total} questões processadas.")

if __name__ == "__main__":
    main()
