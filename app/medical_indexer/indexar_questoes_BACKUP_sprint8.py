import sqlite3
import re
import unicodedata
from pathlib import Path

DB = Path("app/db/planos_aula.db")

DIC = {
    "Cardiologia": {
        "Angina Estável": ["angina", "dor torácica", "isquemia", "coronariana", "dac", "miocárdio", "infarto", "eletrocardiograma", "ecg"],
        "Hipertensão Arterial": ["hipertensão", "pressão arterial", "has", "risco cardiovascular", "anti-hipertensivo"],
        "Insuficiência Cardíaca": ["insuficiência cardíaca", "dispneia", "edema", "fração de ejeção", "congestão"],
    },
    "Endocrinologia": {
        "Diabetes Mellitus": ["diabetes", "glicemia", "hiperglicemia", "insulina", "metformina", "cetoacidose"],
        "Tireoide": ["tireoide", "hipotireoidismo", "hipertireoidismo", "tsh", "t4"],
    },
    "Infectologia": {
        "Sepse": ["sepse", "choque séptico", "infecção", "lactato", "antibiótico", "uti"],
        "Dengue": ["dengue", "arbovirose", "plaquetopenia", "exantema", "aedes"],
    },
    "Pediatria": {
        "Puericultura": ["criança", "lactente", "puericultura", "crescimento", "desenvolvimento"],
        "Neonatologia": ["recém-nascido", "neonato", "apgar", "prematuro"],
    },
    "Ginecologia e Obstetrícia": {
        "Pré-Natal": ["pré-natal", "gestante", "gestação", "gravidez", "obstétrica", "risco gestacional"],
        "Saúde da Mulher": ["mama", "colo uterino", "contracepção", "menopausa", "mulher"],
    },
    "Cirurgia": {
        "Trauma": ["trauma", "atls", "hemorragia", "fratura", "politrauma"],
        "Abdome Agudo": ["abdome agudo", "apendicite", "colecistite", "peritonite"],
    },
    "Saúde Coletiva": {
        "Atenção Primária": ["atenção primária", "aps", "esf", "território", "sus"],
        "Epidemiologia": ["incidência", "prevalência", "risco relativo", "odds", "epidemiologia"],
    },
}

def norm(t):
    t = str(t or "").lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def classificar(texto):
    texto_n = norm(texto)
    hits = []

    for especialidade, temas in DIC.items():
        for tema, palavras in temas.items():
            score = 0
            achadas = []
            for p in palavras:
                pn = norm(p)
                if pn in texto_n:
                    score += 1
                    achadas.append(p)
            if score > 0:
                hits.append((score, especialidade, tema, achadas))

    hits.sort(reverse=True, key=lambda x: x[0])

    if not hits:
        return None

    score, especialidade, tema, achadas = hits[0]

    competencia = "Raciocínio clínico e tomada de decisão"
    habilidade = "Interpretar dados clínicos, reconhecer hipóteses diagnósticas e selecionar condutas."
    descritores = ", ".join(sorted(set(achadas)))

    return especialidade, tema, competencia, habilidade, descritores, score

def garantir_colunas(cur):
    colunas = [r[1] for r in cur.execute("PRAGMA table_info(questoes)").fetchall()]
    novas = {
        "especialidade_indexada": "TEXT",
        "tema_indexado": "TEXT",
        "descritores_indexados": "TEXT",
        "score_indexacao": "REAL",
    }

    for nome, tipo in novas.items():
        if nome not in colunas:
            cur.execute(f"ALTER TABLE questoes ADD COLUMN {nome} {tipo}")

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    garantir_colunas(cur)

    questoes = cur.execute("""
        SELECT id, grande_area, subarea, tema, enunciado,
               alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e,
               comentario, competencia, habilidade
        FROM questoes
        WHERE enunciado IS NOT NULL
          AND TRIM(enunciado) <> ''
    """).fetchall()

    atualizadas = 0

    for q in questoes:
        qid = q[0]
        texto = " ".join(str(x or "") for x in q[1:])
        res = classificar(texto)

        if not res:
            continue

        especialidade, tema_idx, competencia, habilidade, descritores, score = res

        cur.execute("""
            UPDATE questoes
            SET especialidade_indexada = ?,
                tema_indexado = ?,
                descritores_indexados = ?,
                score_indexacao = ?,
                competencia = COALESCE(NULLIF(competencia, ''), ?),
                habilidade = COALESCE(NULLIF(habilidade, ''), ?)
            WHERE id = ?
        """, (
            especialidade,
            tema_idx,
            descritores,
            score,
            competencia,
            habilidade,
            qid
        ))

        atualizadas += 1

    con.commit()

    print(f"Questões analisadas: {len(questoes)}")
    print(f"Questões indexadas/atualizadas: {atualizadas}")

    print("\nAmostra:")
    for r in cur.execute("""
        SELECT id, grande_area, tema, especialidade_indexada, tema_indexado, descritores_indexados, score_indexacao
        FROM questoes
        WHERE tema_indexado IS NOT NULL
        ORDER BY score_indexacao DESC
        LIMIT 15
    """):
        print(r)

    con.close()

if __name__ == "__main__":
    main()
