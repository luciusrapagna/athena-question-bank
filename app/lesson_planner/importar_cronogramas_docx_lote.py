from pathlib import Path
import subprocess
import sys

PASTA = Path("data/entrada/planos_aula")

def main():
    arquivos = sorted(PASTA.glob("*.docx"))

    if not arquivos:
        print(f"Nenhum DOCX encontrado em {PASTA}")
        return

    for i, arquivo in enumerate(arquivos, start=1):
        print(f"\nImportando plano {i}: {arquivo}")
        subprocess.run([
            sys.executable,
            "-m",
            "app.lesson_planner.importar_cronograma_docx",
            str(arquivo),
            "--plano-id",
            str(i),
            "--ano",
            "2026"
        ], check=False)

    print("\nImportação em lote concluída.")

if __name__ == "__main__":
    main()
