import csv
import re
from pathlib import Path

PASTA = Path(__file__).parent
ENTRADA = PASTA / "alunos_baguncados.csv"
SAIDA = PASTA / "notas_processadas.csv"
PENDENTES = PASTA / "registros_pendentes.csv"


def limpar_nome(valor):
    return " ".join((valor or "").split()).title()


def limpar_ra(valor):
    ra = (valor or "").strip().upper()
    ra = re.sub(r"^RA\s*", "", ra)
    ra = re.sub(r"-0$", "", ra)
    ra = ra.lstrip("0")
    return ra


def ler_nota(valor):
    valor = (valor or "").strip().replace(",", ".")
    if not valor or valor.upper() in ("FALTOU", "FALTA", "N/A", "-"):
        return None
    try:
        n = float(valor)
        return n if 0 <= n <= 10 else None
    except ValueError:
        return None


def main():
    if not ENTRADA.exists():
        print(f"Arquivo não encontrado: {ENTRADA.name}")
        return

    prontos = []
    pendentes = []
    ras = set()

    with open(ENTRADA, encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f, delimiter=";")

        for linha, r in enumerate(leitor, start=2):
            nome = limpar_nome(r.get("Nome"))
            ra = limpar_ra(r.get("RA"))
            n1 = ler_nota(r.get("Nota01"))
            n2 = ler_nota(r.get("Nota02") or r.get("Notao2"))
            tf1 = ler_nota(r.get("TF01"))
            tf2 = ler_nota(r.get("TF02"))

            motivos = []
            if not nome:
                motivos.append("Nome ausente")
            if not ra:
                motivos.append("RA ausente")
            elif ra in ras:
                motivos.append("RA duplicado")
            if None in (n1, n2, tf1, tf2):
                motivos.append("Nota ausente ou inválida")
            elif tf1 + tf2 > 2:
                motivos.append("Soma de TF maior que 2")

            registro = {
                "RA": ra,
                "Nome": nome,
                "Nota 1": "" if n1 is None else n1,
                "Nota 2": "" if n2 is None else n2,
                "TF1": "" if tf1 is None else tf1,
                "TF2": "" if tf2 is None else tf2,
                "Nota Final": "",
                "Situação": "",
            }

            if motivos:
                registro["Motivo"] = "; ".join(motivos)
                registro["Linha original"] = linha
                pendentes.append(registro)
                continue

            ras.add(ra)
            final = round(((n1 + n2) / 2) * 0.8 + tf1 + tf2, 2)
            registro["Nota Final"] = f"{final:.2f}"
            registro["Situação"] = "Aprovado" if final >= 7 else "Reprovado"
            prontos.append(registro)

    colunas = [
        "RA", "Nome", "Nota 1", "Nota 2", "TF1", "TF2",
        "Nota Final", "Situação"
    ]

    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(prontos)

    colunas_pendentes = colunas + ["Motivo", "Linha original"]
    with open(PENDENTES, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas_pendentes)
        escritor.writeheader()
        escritor.writerows(pendentes)

    aprovados = sum(r["Situação"] == "Aprovado" for r in prontos)
    print(f"Registros lidos: {len(prontos) + len(pendentes)}")
    print(f"Prontos: {len(prontos)}")
    print(f"Aprovados: {aprovados}")
    print(f"Reprovados: {len(prontos) - aprovados}")
    print(f"Pendentes para revisão: {len(pendentes)}")
    print(f"Arquivos gerados: {SAIDA.name} e {PENDENTES.name}")


if __name__ == "__main__":
    main()