import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path("app/db/planos_aula.db")
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


def campo_vazio(valor):
    return str(valor or "").strip().lower() in ["", "nan", "none", "null"]


def limpar(txt):
    txt = str(txt or "").strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()


def extrair_alternativas(enunciado):
    texto = limpar(enunciado)

    # Remove rodapés comuns
    texto = re.sub(r"Medway\s*-\s*ENARE.*?Páginas?\s*\d+/\d+", " ", texto, flags=re.I)
    texto = limpar(texto)

    # Padrões: A. texto B. texto / A) texto B) texto / A - texto
    padrao = re.compile(
        r"(?<![A-Za-zÀ-ÿ0-9])"
        r"([A-E])\s*[\.\)\-]\s+"
        r"(.+?)"
        r"(?=(?<![A-Za-zÀ-ÿ0-9])[A-E]\s*[\.\)\-]\s+|$)",
        flags=re.I | re.S
    )

    matches = list(padrao.finditer(texto))

    letras = [m.group(1).upper() for m in matches]

    if not all(l in letras for l in ["A", "B", "C", "D", "E"]):
        return None

    alternativas = {}
    for m in matches:
        letra = m.group(1).lower()
        conteudo = limpar(m.group(2))
        alternativas[letra] = conteudo

    if not all(alternativas.get(l) for l in ["a", "b", "c", "d", "e"]):
        return None

    inicio_alt = matches[0].start()
    enunciado_limpo = limpar(texto[:inicio_alt])

    # Evita enunciado curto demais
    if len(enunciado_limpo) < 20:
        return None

    return {
        "enunciado": enunciado_limpo,
        "a": alternativas["a"],
        "b": alternativas["b"],
        "c": alternativas["c"],
        "d": alternativas["d"],
        "e": alternativas["e"],
    }


def main():
    if not DB.exists():
        raise SystemExit(f"Banco não encontrado: {DB}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"planos_aula_backup_antes_separar_alternativas_{stamp}.db"
    shutil.copy2(DB, backup)
    print(f"Backup criado: {backup}")

    con = sqlite3.connect(DB)
    cur = con.cursor()

    questoes = cur.execute("""
        SELECT id, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e
        FROM questoes
        WHERE enunciado IS NOT NULL
          AND TRIM(enunciado) <> ''
    """).fetchall()

    analisadas = 0
    atualizadas = 0
    ignoradas_com_alt = 0
    sem_padrao = 0

    exemplos = []

    for q in questoes:
        qid, enunciado, a, b, c, d, e = q
        analisadas += 1

        if not all(campo_vazio(x) for x in [a, b, c, d, e]):
            ignoradas_com_alt += 1
            continue

        res = extrair_alternativas(enunciado)

        if not res:
            sem_padrao += 1
            continue

        cur.execute("""
            UPDATE questoes
            SET enunciado = ?,
                alternativa_a = ?,
                alternativa_b = ?,
                alternativa_c = ?,
                alternativa_d = ?,
                alternativa_e = ?
            WHERE id = ?
        """, (
            res["enunciado"],
            res["a"],
            res["b"],
            res["c"],
            res["d"],
            res["e"],
            qid
        ))

        atualizadas += 1

        if len(exemplos) < 5:
            exemplos.append((qid, res))

    con.commit()
    con.close()

    print("\nResumo:")
    print(f"Questões analisadas: {analisadas}")
    print(f"Questões atualizadas: {atualizadas}")
    print(f"Ignoradas por já terem alternativas: {ignoradas_com_alt}")
    print(f"Sem padrão A-E detectado: {sem_padrao}")

    print("\nExemplos:")
    for qid, r in exemplos:
        print(f"\nID {qid}")
        print("Enunciado:", r["enunciado"][:250])
        print("A)", r["a"][:120])
        print("B)", r["b"][:120])
        print("C)", r["c"][:120])
        print("D)", r["d"][:120])
        print("E)", r["e"][:120])


if __name__ == "__main__":
    main()
