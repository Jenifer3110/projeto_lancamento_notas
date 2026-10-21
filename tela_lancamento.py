
import csv
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

PASTA = Path(__file__).parent
ARQUIVO = PASTA / "notas_processadas.csv"


def carregar_alunos():
    alunos = {}

    if not ARQUIVO.exists():
        messagebox.showerror(
            "Arquivo não encontrado",
            "Execute automação_notas.py primeiro."
        )
        return alunos

    with open(ARQUIVO, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for aluno in leitor:
            ra = (aluno.get("RA") or "").strip()
            if ra:
                alunos[ra] = aluno

    return alunos


def pesquisar():
    ra = campo_ra.get().strip()

    if not ra:
        messagebox.showwarning("Atenção", "Digite a matrícula do aluno.")
        return

    aluno = alunos.get(ra)

    if aluno is None:
        resultado.config(
            text="Aluno não encontrado nos registros processados.",
            fg="red"
        )
        return

    resultado.config(
        text=(
            f"Nome: {aluno['Nome']}\n"
            f"Matrícula: {aluno['RA']}\n"
            f"Nota final: {aluno['Nota final']}\n"
            f"Situação: {aluno['Situação']}"
        ),
        fg="green"
    )


alunos = carregar_alunos()

janela = tk.Tk()
janela.title("Sistema Simulado de Lançamento de Notas")
janela.geometry("500x350")
janela.resizable(False, False)

titulo = tk.Label(
    janela,
    text="Consulta de Notas dos Alunos",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=20)

tk.Label(janela, text="Digite a matrícula (RA):").pack()

campo_ra = tk.Entry(janela, width=30, font=("Arial", 12))
campo_ra.pack(pady=8)
campo_ra.bind("<Return>", lambda evento: pesquisar())

tk.Button(
    janela,
    text="Pesquisar aluno",
    command=pesquisar,
    width=20
).pack(pady=8)

resultado = tk.Label(
    janela,
    text="Digite uma matrícula para consultar.",
    font=("Arial", 11),
    justify="left"
)
resultado.pack(pady=20)

tk.Label(
    janela,
    text="Ambiente de teste — não conectado a um portal acadêmico real.",
    font=("Arial", 8)
).pack(side="bottom", pady=10)

janela.mainloop()
