import sqlite3
import shutil
import pandas as pd
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
ARQ = Path("outputs/relatorios/candidatas_remocao_hash.csv")
BACKUP_DIR = Path("backups/curadoria")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def backup():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"planos_aula_BACKUP_remocao_hash_{agora}.db"
    shutil.copy2(DB, destino)
    return destino

def remover():
    df = pd.read_csv(ARQ)
    ids = sorted(df["id"].dropna().astype(int).unique().tolist())

    bkp = backup()

    con = sqlite3.connect(DB)
    cur = con.cursor()

    for qid in ids:
        cur.execute("DELETE FROM questoes WHERE id = ?", (qid,))

    con.commit()
    con.close()

    print({
        "backup": str(bkp),
        "removidas": len(ids),
        "mensagem": "Duplicidades exatas por hash removidas com segurança."
    })

if __name__ == "__main__":
    remover()
