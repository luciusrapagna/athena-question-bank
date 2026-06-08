import sqlite3
import shutil
import pandas as pd
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
DUP = Path("outputs/relatorios/relatorio_duplicidades_inteligente.csv")
OUT = Path("outputs/relatorios")
BACKUP_DIR = Path("backups/curadoria")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def backup():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"planos_aula_BACKUP_remover_duplicadas_{agora}.db"
    shutil.copy2(DB, destino)
    return destino

def remover():
    df = pd.read_csv(DUP)
    fortes = df[df["similaridade"] >= 100].copy()

    manter = set(fortes["id_1"])
    remover_ids = sorted(list(set(fortes["id_2"]) - manter))

    rel = fortes[fortes["id_2"].isin(remover_ids)].copy()
    rel.to_csv(OUT / "questoes_removidas_duplicidade_forte.csv", index=False, encoding="utf-8-sig")

    bkp = backup()

    con = sqlite3.connect(DB)
    cur = con.cursor()

    for qid in remover_ids:
        cur.execute("DELETE FROM questoes WHERE id = ?", (int(qid),))

    con.commit()
    con.close()

    print({
        "backup": str(bkp),
        "questoes_removidas": len(remover_ids),
        "relatorio": str(OUT / "questoes_removidas_duplicidade_forte.csv"),
        "mensagem": "Duplicidades fortes removidas com segurança."
    })

if __name__ == "__main__":
    remover()
