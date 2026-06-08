import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
BACKUP_DIR = Path("backups/curadoria")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

REGRAS = [
    {
        "termos": ["pré-natal", "gestante", "gestação", "puerpério", "parto"],
        "competencia": "Atenção integral à saúde da mulher",
        "habilidade": "Reconhecer condições clínicas da gestação, interpretar riscos e indicar condutas adequadas."
    },
    {
        "termos": ["criança", "pediatria", "lactente", "recém-nascido", "adolescente"],
        "competencia": "Atenção integral à saúde da criança e do adolescente",
        "habilidade": "Avaliar crescimento, desenvolvimento, sinais de gravidade e necessidades de cuidado pediátrico."
    },
    {
        "termos": ["sus", "atenção primária", "estratégia saúde da família", "vigilância", "epidemiologia"],
        "competencia": "Atenção à saúde coletiva e vigilância em saúde",
        "habilidade": "Interpretar indicadores, reconhecer necessidades coletivas e propor ações de prevenção e promoção da saúde."
    },
    {
        "termos": ["abdome agudo", "trauma", "hérnia", "apendicite", "colecistite", "cirurgia"],
        "competencia": "Atenção ao paciente cirúrgico",
        "habilidade": "Reconhecer condições cirúrgicas prevalentes, indicar avaliação inicial e definir condutas oportunas."
    },
    {
        "termos": ["sepse", "insuficiência cardíaca", "síndrome coronariana", "diabetes", "hipertensão", "pneumonia"],
        "competencia": "Atenção clínica ao adulto",
        "habilidade": "Interpretar dados clínicos, estabelecer hipóteses diagnósticas e selecionar condutas terapêuticas."
    },
]

def vazio(x):
    return str(x or "").strip() == "" or str(x or "").strip().lower() in ["nan", "none", "null"]

def backup_banco():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"planos_aula_BACKUP_preencher_competencias_{agora}.db"
    shutil.copy2(DB, destino)
    return destino

def inferir(row):
    texto = " ".join([
        str(row.get("enunciado") or ""),
        str(row.get("area") or ""),
        str(row.get("assunto") or ""),
    ]).lower()

    for regra in REGRAS:
        if any(t in texto for t in regra["termos"]):
            return regra["competencia"], regra["habilidade"]

    return (
        "Competência clínica geral",
        "Interpretar dados clínicos, reconhecer hipóteses diagnósticas e selecionar condutas."
    )

def preencher():
    backup = backup_banco()

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("PRAGMA table_info(questoes)")
    colunas = [c[1] for c in cur.fetchall()]

    cur.execute("SELECT * FROM questoes")
    linhas = cur.fetchall()

    atualizadas = 0

    for linha in linhas:
        row = dict(zip(colunas, linha))

        comp_vazia = vazio(row.get("competencia"))
        hab_vazia = vazio(row.get("habilidade"))

        if comp_vazia or hab_vazia:
            competencia, habilidade = inferir(row)

            nova_comp = competencia if comp_vazia else row.get("competencia")
            nova_hab = habilidade if hab_vazia else row.get("habilidade")

            cur.execute("""
                UPDATE questoes
                SET competencia = ?, habilidade = ?
                WHERE id = ?
            """, (nova_comp, nova_hab, row["id"]))

            atualizadas += 1

    con.commit()
    con.close()

    print({
        "backup": str(backup),
        "questoes_atualizadas": atualizadas,
        "mensagem": "Competências e habilidades preenchidas por curadoria inteligente."
    })

if __name__ == "__main__":
    preencher()
