from tkinter import Tk, filedialog

root = Tk()
root.withdraw()
root.attributes("-topmost", True)

arquivo = filedialog.askopenfilename(
    title="Selecione uma prova ou plano",
    filetypes=[
        ("PDF", "*.pdf"),
        ("Word", "*.docx"),
        ("Excel", "*.xlsx"),
        ("Todos os arquivos", "*.*")
    ]
)

print("Arquivo selecionado:")
print(arquivo)

root.destroy()
