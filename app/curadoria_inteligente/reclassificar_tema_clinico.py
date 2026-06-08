import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
BACKUP_DIR = Path("backups/curadoria")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

REGRAS = [
    ("Sepse", ["sepse", "choque séptico", "lactato", "qsofa", "sofa"]),
    ("Pneumonia", ["pneumonia", "consolidação", "derrame pleural", "escarro", "dispneia", "tosse"]),
    ("Síndrome coronariana", ["infarto", "iam", "supra", "st", "troponina", "dor torácica", "angina"]),
    ("Insuficiência cardíaca", ["insuficiência cardíaca", "ic", "edema", "ortopneia", "fração de ejeção"]),
    ("Hipertensão arterial", ["hipertensão", "has", "pressão arterial", "pa elevada"]),
    ("Diabetes mellitus", ["diabetes", "glicemia", "hiperglicemia", "insulina", "hemoglobina glicada"]),
    ("AVC", ["avc", "acidente vascular", "hemiparesia", "afasia", "trombólise"]),
    ("DPOC/Asma", ["dpoc", "asma", "broncoespasmo", "sibilância", "beta-agonista"]),
    ("Tuberculose", ["tuberculose", "baciloscopia", "rifampicina", "isoniazida"]),
    ("Doença renal", ["creatinina", "ureia", "injúria renal", "doença renal", "hemodiálise"]),
    ("Anemias", ["anemia", "hemoglobina", "ferritina", "microcítica", "macrocítica"]),
    ("HIV/IST", ["hiv", "aids", "sífilis", "gonorreia", "clamídia", "ist"]),
    ("Doenças gastrointestinais", ["diarreia", "vômitos", "dor abdominal", "gastrite", "hepatite", "cirrose"]),
    ("Endocrinologia", ["tireoide", "hipotireoidismo", "hipertireoidismo", "cortisol", "adrenal"]),
    ("Saúde mental", ["depressão", "ansiedade", "psicose", "transtorno bipolar", "suicídio"]),
]

def backup():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"planos_aula_BACKUP_reclassificacao_tema_clinico_{agora}.db"
    shutil.copy2(DB, destino)
    return destino

def reclassificar():
    bkp = backup()

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        SELECT id, enunciado, assunto
        FROM questoes
        WHERE assunto = 'Tema clínico geral'
    """)
    linhas = cur.fetchall()

    atualizadas = 0
    sem_regra = 0

    for qid, enunciado, assunto in linhas:
        texto = str(enunciado or "").lower()
        novo_assunto = None

        for assunto_regra, termos in REGRAS:
            if any(t in texto for t in termos):
                novo_assunto = assunto_regra
                break

        if novo_assunto:
            cur.execute("""
                UPDATE questoes
                SET assunto = ?
                WHERE id = ?
            """, (novo_assunto, qid))
            atualizadas += 1
        else:
            sem_regra += 1

    con.commit()
    con.close()

    print({
        "backup": str(bkp),
        "tema_clinico_geral_encontradas": len(linhas),
        "reclassificadas": atualizadas,
        "mantidas_sem_regra": sem_regra
    })

if __name__ == "__main__":
    reclassificar()
PYcat > app/curadoria_inteligente/reclassificar_tema_clinico.py <<'PY'
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
BACKUP_DIR = Path("backups/curadoria")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

REGRAS = [
    ("Sepse", ["sepse", "choque séptico", "lactato", "qsofa", "sofa"]),
    ("Pneumonia", ["pneumonia", "consolidação", "derrame pleural", "escarro", "dispneia", "tosse"]),
    ("Síndrome coronariana", ["infarto", "iam", "supra", "st", "troponina", "dor torácica", "angina"]),
    ("Insuficiência cardíaca", ["insuficiência cardíaca", "ic", "edema", "ortopneia", "fração de ejeção"]),
    ("Hipertensão arterial", ["hipertensão", "has", "pressão arterial", "pa elevada"]),
    ("Diabetes mellitus", ["diabetes", "glicemia", "hiperglicemia", "insulina", "hemoglobina glicada"]),
    ("AVC", ["avc", "acidente vascular", "hemiparesia", "afasia", "trombólise"]),
    ("DPOC/Asma", ["dpoc", "asma", "broncoespasmo", "sibilância", "beta-agonista"]),
    ("Tuberculose", ["tuberculose", "baciloscopia", "rifampicina", "isoniazida"]),
    ("Doença renal", ["creatinina", "ureia", "injúria renal", "doença renal", "hemodiálise"]),
    ("Anemias", ["anemia", "hemoglobina", "ferritina", "microcítica", "macrocítica"]),
    ("HIV/IST", ["hiv", "aids", "sífilis", "gonorreia", "clamídia", "ist"]),
    ("Doenças gastrointestinais", ["diarreia", "vômitos", "dor abdominal", "gastrite", "hepatite", "cirrose"]),
    ("Endocrinologia", ["tireoide", "hipotireoidismo", "hipertireoidismo", "cortisol", "adrenal"]),
    ("Saúde mental", ["depressão", "ansiedade", "psicose", "transtorno bipolar", "suicídio"]),
]

def backup():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"planos_aula_BACKUP_reclassificacao_tema_clinico_{agora}.db"
    shutil.copy2(DB, destino)
    return destino

def reclassificar():
    bkp = backup()

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        SELECT id, enunciado, assunto
        FROM questoes
        WHERE assunto = 'Tema clínico geral'
    """)
    linhas = cur.fetchall()

    atualizadas = 0
    sem_regra = 0

    for qid, enunciado, assunto in linhas:
        texto = str(enunciado or "").lower()
        novo_assunto = None

        for assunto_regra, termos in REGRAS:
            if any(t in texto for t in termos):
                novo_assunto = assunto_regra
                break

        if novo_assunto:
            cur.execute("""
                UPDATE questoes
                SET assunto = ?
                WHERE id = ?
            """, (novo_assunto, qid))
            atualizadas += 1
        else:
            sem_regra += 1

    con.commit()
    con.close()

    print({
        "backup": str(bkp),
        "tema_clinico_geral_encontradas": len(linhas),
        "reclassificadas": atualizadas,
        "mantidas_sem_regra": sem_regra
    })

if __name__ == "__main__":
    reclassificar()
