import csv
import time
import webbrowser
from pathlib import Path
import pyautogui

PASTA = Path(__file__).parent
ARQUIVO = PASTA / "alunos_baguncados.csv"
CONTROLE = PASTA / "lancamentos_simulados.csv"

FORMULARIO = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSecZ46FOLWp1YTA5PB7Kvq36G6n_08XrT3Su9SSTaQx-33gTw/viewform"
)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def nota(valor):
    valor = (valor or "").strip().replace(",", ".")
    if not valor or valor.upper() in ("FALTOU", "FALTA", "N/A", "-"):
        return None
    try:
        n = float(valor)
        return n if 0 <= n <= 10 else None
    except ValueError:
        return None


def ra_limpo(valor):
    ra = (valor or "").strip().upper().replace("RA", "").strip()
    if ra.endswith("-0"):
        ra = ra[:-2]
    return ra.lstrip("0")


def carregar():
    with open(ARQUIVO, encoding="utf-8-sig", newline="") as f:
        registros = csv.DictReader(f, delimiter=";")
        resultado = []
        vistos = set()

        for r in registros:
            ra = ra_limpo(r.get("RA"))
            nome = " ".join((r.get("Nome") or "").split()).title()
            n1 = nota(r.get("Nota01"))
            n2 = nota(r.get("Nota02") or r.get("Notao2"))
            tf1 = nota(r.get("TF01"))
            tf2 = nota(r.get("TF02"))

            if not ra or not nome or None in (n1, n2, tf1, tf2):
                continue
            if tf1 + tf2 > 2 or ra in vistos:
                continue

            vistos.add(ra)
            final = round(((n1 + n2) / 2) * 0.8 + tf1 + tf2, 2)
            resultado.append({
                "RA": ra,
                "Nome": nome,
                "Nota 1": n1,
                "Nota 2": n2,
                "TF1": tf1,
                "TF2": tf2,
                "Nota Final": final,
            })

    return resultado


def registrar(aluno, status):
    existe = CONTROLE.exists() and CONTROLE.stat().st_size > 0
    with open(CONTROLE, "a", newline="", encoding="utf-8-sig") as f:
        campos = ["RA", "Nome", "Nota Final", "Status"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            escritor.writeheader()
        escritor.writerow({
            "RA": aluno["RA"],
            "Nome": aluno["Nome"],
            "Nota Final": f"{aluno['Nota Final']:.2f}",
            "Status": status,
        })


def main():
    if not ARQUIVO.exists():
        print(f"Arquivo não encontrado: {ARQUIVO}")
        input("Enter para sair.")
        return

    alunos = carregar()
    print(f"Registros válidos encontrados: {len(alunos)}")

    if not alunos:
        input("Nenhum registro válido. Enter para sair.")
        return

    print("\nO robô preencherá e tentará enviar cada formulário.")
    print("Não execute novamente sem conferir a planilha para evitar duplicações.")
    if input("Digite TESTAR para continuar: ").strip().upper() != "TESTAR":
        return

    webbrowser.open(FORMULARIO)
    input(
        "\nQuando o Forms abrir, clique no campo RA. "
        "Depois volte para este terminal sem mover o mouse e pressione Enter."
    )

    # Guarda a posição onde o cursor está; use o campo RA na configuração.
    x, y = pyautogui.position()
    print(f"Posição inicial configurada: ({x}, {y})")
    print("Começando em 5 segundos...")
    time.sleep(5)

    for i, aluno in enumerate(alunos, 1):
        print(f"\n{i}/{len(alunos)}: {aluno['RA']} - {aluno['Nome']}")

        try:
            pyautogui.click(x, y)
            valores = [
                aluno["RA"],
                aluno["Nome"],
                str(aluno["Nota 1"]).replace(".", ","),
                str(aluno["Nota 2"]).replace(".", ","),
                str(aluno["TF1"]).replace(".", ","),
                str(aluno["TF2"]).replace(".", ","),
                f"{aluno['Nota Final']:.2f}".replace(".", ","),
            ]

            for valor in valores:
                pyautogui.write(valor, interval=0.03)
                pyautogui.press("tab")
                time.sleep(0.2)

            # O foco pode variar conforme a estrutura do formulário.
            # Confira o primeiro envio antes de permitir o restante.
            if i == 1:
                print(
                    "\nPrimeiro aluno preenchido. Confira os campos no navegador."
                    "\nSe estiverem corretos e o foco estiver no botão Enviar,"
                    " pressione Enter no terminal para tentar enviar."
                )
                input()
                pyautogui.press("enter")
                time.sleep(4)
                registrar(aluno, "Tentativa de envio; confirmar na planilha")

                if input(
                    "Confira se a resposta chegou à planilha. "
                    "Digite SIM para continuar ou qualquer outra coisa para parar: "
                ).strip().upper() != "SIM":
                    print("Parado para conferência. Não execute novamente sem revisar.")
                    break
            else:
                pyautogui.press("enter")
                time.sleep(4)
                registrar(aluno, "Tentativa de envio; confirmar na planilha")

            if i < len(alunos):
                pyautogui.hotkey("ctrl", "l")
                pyautogui.write(FORMULARIO, interval=0.01)
                pyautogui.press("enter")
                time.sleep(5)

        except pyautogui.FailSafeException:
            print("Interrompido pelo movimento do mouse para o canto superior esquerdo.")
            break
        except Exception as erro:
            print(f"Erro: {erro}")
            break

    print("\nFim da execução. Confira as respostas na planilha vinculada.")
    input("Pressione Enter para fechar.")


if __name__ == "__main__":
    main()