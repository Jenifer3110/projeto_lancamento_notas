
import csv
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import pyautogui

PASTA = Path(__file__).parent
ARQUIVO = PASTA / "notas_processadas.csv"
SAIDA = PASTA / "lancamentos_simulados.csv"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


def carregar_alunos():
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            "Execute automação_notas.py antes de iniciar o robô."
        )

    with open(ARQUIVO, encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


try:
    alunos = carregar_alunos()
except Exception as erro:
    messagebox.showerror("Erro", str(erro))
    raise SystemExit


janela = tk.Tk()
janela.title("Portal Acadêmico Simulado - Laboratório 07")
janela.geometry("850x650+50+50")
janela.configure(padx=25, pady=20)

tk.Label(
    janela,
    text="PORTAL ACADÊMICO — AMBIENTE DE TESTE",
    font=("Arial", 16, "bold")
).pack(pady=10)

tk.Label(janela, text="Matrícula (RA):").pack(anchor="w")
campo_ra = tk.Entry(janela, font=("Arial", 12), width=35)
campo_ra.pack(anchor="w", pady=5)

aluno_atual = {"dados": None}

def pesquisar_aluno():
    ra = campo_ra.get().strip()

    encontrado = next(
        (a for a in alunos if a.get("RA", "").strip() == ra),
        None
    )

    if encontrado is None:
        aluno_atual["dados"] = None
        resultado.config(text="Aluno não encontrado.", fg="red")
        return

    aluno_atual["dados"] = encontrado
    resultado.config(
        text=f"Aluno: {encontrado['Nome']}\n"
             f"Matrícula: {encontrado['RA']}\n"
             "Registro localizado. Digite a nota final.",
        fg="black"
    )


tk.Button(
    janela, text="Buscar matrícula",
    command=pesquisar_aluno, width=22
).pack(anchor="w", pady=5)

resultado = tk.Label(
    janela, text="Aguardando pesquisa...",
    font=("Arial", 11), justify="left"
)
resultado.pack(anchor="w", pady=15)

tk.Label(janela, text="Nota final para lançamento:").pack(anchor="w")
campo_nota = tk.Entry(janela, font=("Arial", 12), width=20)
campo_nota.pack(anchor="w", pady=5)

log = tk.Text(janela, height=9, width=85, state="disabled")
log.pack(pady=15)

def registrar_log(mensagem):
    log.config(state="normal")
    log.insert("end", mensagem + "\n")
    log.see("end")
    log.config(state="disabled")


def salvar_nota():
    aluno = aluno_atual["dados"]

    if not aluno:
        messagebox.showwarning(
            "Atenção", "Pesquise um aluno antes de salvar."
        )
        return

    texto = campo_nota.get().strip().replace(",", ".")

    try:
        nota = float(texto)
        if not 0 <= nota <= 10:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Nota inválida", "Digite uma nota entre 0 e 10."
        )
        return

    existe = SAIDA.exists()

    with open(SAIDA, "a", newline="", encoding="utf-8-sig") as arquivo:
        colunas = ["RA", "Nome", "Nota lançada", "Situação"]
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)

        if not existe or SAIDA.stat().st_size == 0:
            escritor.writeheader()

        escritor.writerow({
            "RA": aluno["RA"],
            "Nome": aluno["Nome"],
            "Nota lançada": f"{nota:.2f}",
            "Situação": "Aprovado" if nota >= 7 else "Reprovado"
        })

    registrar_log(
        f"Salvo no simulador: {aluno['RA']} - "
        f"{aluno['Nome']} - Nota {nota:.2f}"
    )

    aluno_atual["dados"] = None
    campo_ra.delete(0, "end")
    campo_nota.delete(0, "end")
    resultado.config(text="Registro salvo. Aguardando próximo aluno.")


tk.Button(
    janela, text="Salvar lançamento",
    command=salvar_nota, width=22
).pack(anchor="w", pady=5)

indice = 0
executando = False


def clicar_no_centro(widget):
    janela.update_idletasks()
    x = widget.winfo_rootx() + widget.winfo_width() // 2
    y = widget.winfo_rooty() + widget.winfo_height() // 2
    pyautogui.click(x, y)


def iniciar_ciclo():
    global indice, executando

    if not executando:
        return

    if indice >= len(alunos):
        executando = False
        registrar_log("Automação concluída.")
        messagebox.showinfo(
            "Concluído",
            f"Robô terminou. Registros processados: {indice}.\n"
            "Confira lancamentos_simulados.csv."
        )
        return

    aluno = alunos[indice]

    clicar_no_centro(campo_ra)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.write(aluno["RA"].strip())
    clicar_no_centro(botao_buscar)

    janela.after(600, preencher_nota)


def preencher_nota():
    if not executando:
        return

    aluno = alunos[indice]

    clicar_no_centro(campo_nota)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.write(str(aluno["Nota final"]))
    clicar_no_centro(botao_salvar)

    janela.after(500, proximo_aluno)


def proximo_aluno():
    global indice
    indice += 1
    janela.after(300, iniciar_ciclo)


def iniciar_robo():
    global indice, executando

    if not alunos:
        messagebox.showwarning(
            "Sem dados", "Não há alunos em notas_processadas.csv."
        )
        return

    confirmar = messagebox.askyesno(
        "Iniciar automação",
        f"O robô vai lançar {len(alunos)} registros neste "
        "portal SIMULADO. Deseja continuar?"
    )

    if confirmar:
        indice = 0
        executando = True
        janela.after(1000, iniciar_ciclo)


botao_buscar = janela.winfo_children()[2]
botao_salvar = None

# Referências explícitas aos botões para o PyAutoGUI.
for widget in janela.winfo_children():
    if isinstance(widget, tk.Button):
        if widget.cget("text") == "Buscar matrícula":
            botao_buscar = widget
        elif widget.cget("text") == "Salvar lançamento":
            botao_salvar = widget

# O robô usa estas referências durante a automação.
botao_buscar = botao_buscar
botao_salvar = botao_salvar

botao_robo = tk.Button(
    janela,
    text="INICIAR ROBÔ PYAutoGUI",
    command=iniciar_robo,
    font=("Arial", 12, "bold"),
    width=28
)
botao_robo.pack(pady=10)

# A função de preenchimento usa o botão de salvamento real.
botao_salvar_original = botao_salvar
botao_salvar = botao_salvar_original

janela.mainloop()
