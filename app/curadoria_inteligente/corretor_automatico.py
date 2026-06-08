import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
BACKUP_DIR = Path("backups/curadoria")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def normalizar_texto(valor):
    if valor is None:
        return ""

    texto = str(valor)

    ruins = ["nan", "None", "NULL", "null"]
    for r in ruins:
        if texto.strip() == r:
            return ""

    texto = texto.replace("  ", " ").strip()
    return texto

def backup_banco():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"planos_aula_BACKUP_curadoria_{agora}.db"
    shutil.copy2(DB, destino)
    return destino

def corrigir():
    backup = backup_banco()

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("PRAGMA table_info(questoes)")
    colunas = [c[1] for c in cur.fetchall()]

    campos_texto = [
        c for c in colunas
        if c in [
            "enunciado",
            "area",
            "assunto",
            "competencia",
            "habilidade",
            "alternativas",
            "alternativa_a",
            "alternativa_b",
            "alternativa_c",
            "alternativa_d",
            "alternativa_e",
            "resposta",
            "comentario",
            "justificativa",
        ]
    ]

    cur.execute("SELECT * FROM questoes")
    linhas = cur.fetchall()

    corrigidas = 0

    for linha in linhas:
        registro = dict(zip(colunas, linha))
        updates = {}

        for campo in campos_texto:
            original = registro.get(campo)
            novo = normalizar_texto(original)

            if str(original or "") != str(novo or ""):
                updates[campo] = novo

        if updates:
            set_sql = ", ".join([f"{campo}=?" for campo in updates])
            valores = list(updates.values())
            valores.append(registro["id"])

            cur.execute(
                f"UPDATE questoes SET {set_sql} WHERE id=?",
                valores
            )
            corrigidas += 1

    con.commit()
    con.close()

    print({
        "backup": str(backup),
        "corrigidas": corrigidas,
        "mensagem": "Correção automática concluída com segurança."
    })

if __name__ == "__main__":
    corrigir()
