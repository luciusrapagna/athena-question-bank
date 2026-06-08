import sqlite3
import re
import json
from pathlib import Path

from app.medical_translator.tradutor_icd10 import (
    classificar_por_nome,
    classificar_por_dicionario,
)

DB = "app/db/planos_aula.db"
DICIONARIO_PATH = Path("data/dicionarios/athena_medical_dictionary.json")
HABILIDADE_PADRAO = "Interpretar dados clínicos, reconhecer hipóteses diagnósticas e selecionar condutas."

COMPETENCIAS = {
    "Clínica Médica": "Cuidado integral do adulto e raciocínio clínico",
    "Cirurgia": "Avaliação, decisão e manejo de condições cirúrgicas",
    "Pediatria": "Atenção integral à saúde da criança e do adolescente",
    "Ginecologia e Obstetrícia": "Atenção integral à saúde da mulher, gestação e parto",
    "Saúde Coletiva": "Atenção primária, vigilância, SUS e saúde coletiva",
}

def normalizar(txt):
    return re.sub(r"\s+", " ", str(txt or "").lower()).strip()

def carregar_dicionario():
    with open(DICIONARIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def texto_questao(row):
    campos = [
        "enunciado", "alternativa_a", "alternativa_b", "alternativa_c",
        "alternativa_d", "alternativa_e"
    ]
    return " ".join(str(row.get(c) or "") for c in campos)

def classificar_dicionario_athena(texto, area_original, dicionario):
    texto_n = normalizar(texto)
    melhor = None

    for area, dados_area in dicionario.items():
        competencia = dados_area.get("competencia", COMPETENCIAS.get(area, ""))
        for especialidade, temas in dados_area.get("especialidades", {}).items():
            for tema, termos in temas.items():
                pontos = 0
                termos_encontrados = []

                for termo in termos:
                    termo_n = normalizar(termo)
                    if termo_n and termo_n in texto_n:
                        peso = 5 if len(termo_n.split()) >= 2 else 2
                        pontos += peso
                        termos_encontrados.append(termo)

                if area_original == area:
                    pontos += 1

                if pontos > 0:
                    candidato = {
                        "area": area,
                        "especialidade": especialidade,
                        "tema": tema,
                        "competencia": competencia,
                        "habilidade": HABILIDADE_PADRAO,
                        "score": pontos,
                        "descritores": "; ".join(termos_encontrados),
                        "fonte_indexacao": "athena_medical_dictionary"
                    }

                    if melhor is None or candidato["score"] > melhor["score"]:
                        melhor = candidato

    return melhor

def classificar_translator(texto):
    cls = classificar_por_nome(texto)
    fonte = "translator_nome"

    if not cls:
        cls = classificar_por_dicionario(texto)
        fonte = "translator_specialty_dictionary"

    if not cls:
        return None

    return {
        "area": cls.get("area", ""),
        "especialidade": cls.get("especialidade", ""),
        "tema": cls.get("especialidade", "Tema clínico geral"),
        "competencia": cls.get("competencia", ""),
        "habilidade": cls.get("habilidade", HABILIDADE_PADRAO),
        "score": 1.5,
        "descritores": "",
        "fonte_indexacao": fonte
    }


def hipertensao_fraca(texto, c):
    if not c or c.get("tema") != "Hipertensão arterial":
        return False

    t = normalizar(texto)

    fortes = [
        "hipertensão arterial",
        "crise hipertensiva",
        "emergência hipertensiva",
        "urgência hipertensiva",
        "anti-hipertensivo",
        "hipertenso conhecido",
        "história de hipertensão",
        "diagnóstico de hipertensão",
        "tratamento da hipertensão"
    ]

    if any(f in t for f in fortes):
        return False

    return True


def classificar(texto, area_original, dicionario):
    c1 = classificar_dicionario_athena(texto, area_original, dicionario)

    if hipertensao_fraca(texto, c1):
        c1 = None

    c2 = classificar_translator(texto)

    if c1 and c2:
        # Mantém o tema mais específico do dicionário ATHENA,
        # mas usa área/especialidade do Translator quando a classificação antiga era genérica.
        if c1["tema"] == "Tema clínico geral" or c1["score"] < 2:
            return c2
        return c1

    if c1:
        return c1

    if c2:
        return c2

    if area_original in dicionario:
        return {
            "area": area_original,
            "especialidade": area_original,
            "tema": "Tema clínico geral",
            "competencia": dicionario[area_original].get("competencia", COMPETENCIAS.get(area_original, "")),
            "habilidade": HABILIDADE_PADRAO,
            "score": 0.1,
            "descritores": "",
            "fonte_indexacao": "fallback_area_original"
        }

    return {
        "area": "Clínica Médica",
        "especialidade": "Clínica Médica Geral",
        "tema": "Tema clínico geral",
        "competencia": COMPETENCIAS["Clínica Médica"],
        "habilidade": HABILIDADE_PADRAO,
        "score": 0.05,
        "descritores": "",
        "fonte_indexacao": "fallback_default"
    }

def garantir_coluna(cur, tabela, coluna, tipo="TEXT"):
    cur.execute(f"PRAGMA table_info({tabela})")
    cols = [r[1] for r in cur.fetchall()]
    if coluna not in cols:
        cur.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")

def main():
    dicionario = carregar_dicionario()

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    garantir_coluna(cur, "questoes", "fonte_indexacao_medica", "TEXT")

    cur.execute("SELECT * FROM questoes")
    questoes = cur.fetchall()

    total = 0

    for q in questoes:
        d = dict(q)
        area_original = d.get("grande_area") or d.get("area") or ""
        c = classificar(texto_questao(d), area_original, dicionario)

        cur.execute("""
            UPDATE questoes
            SET grande_area = ?,
                area = ?,
                assunto = ?,
                tema_indexado = ?,
                especialidade = ?,
                subtema_indexado = ?,
                competencia_enamed = ?,
                habilidade_enamed = ?,
                descritores_indexados = ?,
                confianca_indexacao = ?,
                fonte_indexacao_medica = ?
            WHERE id = ?
        """, (
            c["area"], c["area"], c["tema"], c["tema"],
            c["especialidade"], c["tema"],
            c["competencia"], c["habilidade"],
            c["descritores"], c["score"],
            c["fonte_indexacao"], d["id"]
        ))

        total += 1

    con.commit()
    con.close()
    print(f"Indexação ATHENA + Translator concluída: {total} questões processadas.")

if __name__ == "__main__":
    main()
