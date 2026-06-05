import sqlite3
import re

DB_PATH = "app/db/planos_aula.db"

REGRAS = {
    "Clínica Médica": {
        "Cardiologia": ["infarto", "iam", "ecg", "troponina", "angina", "hipertensão", "has", "insuficiência cardíaca", "arritmia"],
        "Pneumologia": ["asma", "dpoc", "dispneia", "pneumonia", "tuberculose", "espirometria", "tosse"],
        "Nefrologia": ["creatinina", "rim", "renal", "acidose", "hemodiálise", "proteinúria", "lesão renal"],
        "Endocrinologia": ["diabetes", "glicemia", "insulina", "tireoide", "hipotireoidismo", "hipertireoidismo"],
        "Gastroenterologia": ["diarreia", "vômito", "hepatite", "cirrose", "dor abdominal", "hemorragia digestiva"],
        "Infectologia": ["febre", "sepse", "antibiótico", "hiv", "dengue", "malária", "infecção"]
    },
    "Cirurgia": {
        "Trauma": ["trauma", "politrauma", "glasgow", "hemorragia", "fratura"],
        "Abdome Agudo": ["apendicite", "abdome agudo", "colecistite", "peritonite", "obstrução intestinal"],
        "Pré e Pós-operatório": ["pré-operatório", "pós-operatório", "cirurgia", "anestesia", "complicação cirúrgica"]
    },
    "Pediatria": {
        "Neonatologia": ["recém-nascido", "neonato", "prematuro", "apgar", "icterícia neonatal"],
        "Puericultura": ["puericultura", "crescimento", "desenvolvimento", "aleitamento", "vacinação"],
        "Emergências Pediátricas": ["lactente", "criança", "desidratação", "convulsão febril", "bronquiolite"]
    },
    "Ginecologia e Obstetrícia": {
        "Obstetrícia": ["gestante", "gravidez", "pré-natal", "parto", "puerpério", "eclâmpsia", "pré-eclâmpsia"],
        "Ginecologia": ["endometriose", "colo uterino", "dismenorreia", "contracepção", "sangramento uterino"],
        "Saúde da Mulher": ["mama", "mamografia", "climatério", "menopausa", "preventivo"]
    },
    "Saúde Coletiva": {
        "Epidemiologia": ["incidência", "prevalência", "risco relativo", "odds ratio", "epidemiologia"],
        "Atenção Primária": ["ubs", "atenção primária", "aps", "território", "estratégia saúde da família"],
        "SUS e Políticas de Saúde": ["sus", "integralidade", "equidade", "universalidade", "política nacional"],
        "Vigilância em Saúde": ["notificação", "vigilância", "surto", "dengue", "imunização"]
    }
}

def normalizar(texto):
    texto = (texto or "").lower()
    texto = re.sub(r"[^a-zà-ÿ0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def classificar(texto):
    texto = normalizar(texto)

    melhor_area = None
    melhor_tema = None
    melhor_score = 0

    for area, temas in REGRAS.items():
        for tema, termos in temas.items():
            score = sum(1 for termo in termos if termo in texto)
            if score > melhor_score:
                melhor_score = score
                melhor_area = area
                melhor_tema = tema

    return melhor_area, melhor_tema, melhor_score

def executar():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    questoes = cur.execute("""
        SELECT id, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e
        FROM questoes
    """).fetchall()

    classificadas = 0
    sem_classificacao = 0

    for q in questoes:
        questao_id = q[0]
        texto = " ".join(str(x or "") for x in q[1:])

        area, tema, score = classificar(texto)

        if area and tema:
            cur.execute("""
                UPDATE questoes
                SET grande_area = ?,
                    subarea = ?,
                    tema = ?
                WHERE id = ?
            """, (area, tema, tema, questao_id))
            classificadas += 1
        else:
            sem_classificacao += 1

    con.commit()
    con.close()

    print(f"Classificadas: {classificadas}")
    print(f"Sem classificação: {sem_classificacao}")

if __name__ == "__main__":
    executar()
