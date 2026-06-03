from tkinter import Tk, filedialog
import fitz

root = Tk()
root.withdraw()
root.attributes("-topmost", True)

pdf_path = filedialog.askopenfilename(
    title="Selecione o PDF da prova",
    filetypes=[("PDF","*.pdf")]
)

root.destroy()

if not pdf_path:
    print("Nenhum PDF selecionado.")
    raise SystemExit

print(f"PDF selecionado: {pdf_path}")

pdf = fitz.open(pdf_path)

for page_num, page in enumerate(pdf, start=1):

    print(f"\n{'='*80}")
    print(f"PAGINA {page_num}")
    print(f"{'='*80}")

    blocks = page.get_text("blocks")

    for b in sorted(blocks, key=lambda x: (x[1], x[0])):

        x0,y0,x1,y1,text = b[:5]

        text = text.strip().replace("\n"," ")

        if not text:
            continue

        print(
            f"X={x0:7.1f} "
            f"Y={y0:7.1f} "
            f"X2={x1:7.1f} "
            f"Y2={y1:7.1f} "
            f"-> {text[:150]}"
        )
