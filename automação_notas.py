
import csv
from pathlib import Path
from collections import Counter

PASTA = Path(__file__).parent
ARQUIVO_ENTRADA = PASTA / "alunos_baguncados.csv"
ARQUIVO_VALIDOS = PASTA / "notas_processadas.csv"
ARQUIVO_PENDENCIAS = PASTA / "registros_pendentes.csv"


def limpar_texto(valor):
    return " ".join((valor or "").strip().split())


def ler_nota(valor):
    texto = limpar_texto(valor).replace(",", ".")

    if not texto or texto.upper() in {
        "FALTOU", "FALTA", "N/A", "-", "NA"
    }:
        return None

    try:
        nota = float(texto)
    except ValueError:
        return None

    if not 0 <= nota <= 10:
        return None

    return nota


def processar():
    if not ARQUIVO_ENTRADA.exists():
        print("ERRO: não encontrei alunos_baguncados.csv.")
        return

    validos = []
    pendencias = []
    ras_encontrados = set()
    duplicados = set()
    total = 0

    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8-sig",
              newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        if not leitor.fieldnames:
            print("ERRO: o CSV está vazio ou sem cabeçalho.")
            return

        # Aceita variações comuns no nome da coluna Nota 2.
        colunas = {
            limpar_texto(nome).lower().replace(" ", "").replace("_", ""):
            nome
            for nome in leitor.fieldnames
            if nome
        }

        aliases = {
            "nome": ["nome"],
            "ra": ["ra", "matricula", "matrícula"],
            "nota1": ["nota01", "nota1"],
            "tf1": ["tf01", "tf1"],
            "nota2": ["notao2", "nota02", "nota2"],
            "tf2": ["tf02", "tf2"],
        }

        mapa = {}
        for campo, opcoes in aliases.items():
            for opcao in opcoes:
                if opcao in colunas:
                    mapa[campo] = colunas[opcao]
                    break

        obrigatorias = ["nome", "ra", "nota1", "tf1", "nota2", "tf2"]
        faltando = [c for c in obrigatorias if c not in mapa]

        if faltando:
            print("ERRO: não encontrei estas colunas:", ", ".join(faltando))
            print("Confira se o cabeçalho está separado por ponto e vírgula.")
            return

        for numero_linha, linha in enumerate(leitor, start=2):
            if not any(limpar_texto(v) for v in linha.values() if v):
                continue

            total += 1
            problemas = []

            nome_original = limpar_texto(linha.get(mapa["nome"]))
            nome = nome_original.title()

            ra_original = limpar_texto(linha.get(mapa["ra"]))
            ra = ra_original.upper().replace(" ", "")

            if ra.startswith("RA"):
                ra = ra[2:]

            if not nome:
                problemas.append("Nome ausente")

            if not ra:
                problemas.append("RA ausente")
            elif not ra.isdigit():
                problemas.append("RA fora do formato esperado")

            if ra and ra in ras_encontrados:
                duplicados.add(ra)
                problemas.append("RA duplicado")
            elif ra and ra.isdigit():
                ras_encontrados.add(ra)

            notas = {}
            for campo, rotulo in [
                ("nota1", "Nota01"),
                ("tf1", "TF01"),
                ("nota2", "Nota02"),
                ("tf2", "TF02"),
            ]:
                valor_original = limpar_texto(linha.get(mapa[campo]))
                nota = ler_nota(valor_original)
                notas[campo] = nota

                if nota is None:
                    problemas.append(f"{rotulo} ausente ou inválida")

            resultado = {
                "Linha original": numero_linha,
                "Nome": nome,
                "RA": ra_original,
                "Nota01": limpar_texto(linha.get(mapa["nota1"])),
                "TF01": limpar_texto(linha.get(mapa["tf1"])),
                "Nota02": limpar_texto(linha.get(mapa["nota2"])),
                "TF02": limpar_texto(linha.get(mapa["tf2"])),
            }

            if problemas:
                resultado["Problemas"] = "; ".join(problemas)
                pendencias.append(resultado)
                continue

            media_notas = (notas["nota1"] + notas["nota2"]) / 2
            media_tf = (notas["tf1"] + notas["tf2"]) / 2

            # Hipótese: notas principais peso 8 e TF peso 2.
            nota_final = round((media_notas * 8 + media_tf * 2) / 10, 2)

            resultado.update({
                "Nota01": notas["nota1"],
                "TF01": notas["tf1"],
                "Nota02": notas["nota2"],
                "TF02": notas["tf2"],
                "Nota final": nota_final,
                "Situação": (
                    "Aprovado" if nota_final >= 7 else "Reprovado"
                ),
            })
            validos.append(resultado)

    colunas_validos = [
        "Linha original", "Nome", "RA", "Nota01", "TF01",
        "Nota02", "TF02", "Nota final", "Situação"
    ]
    colunas_pendencias = [
        "Linha original", "Nome", "RA", "Nota01", "TF01",
        "Nota02", "TF02", "Problemas"
    ]

    with open(ARQUIVO_VALIDOS, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas_validos)
        escritor.writeheader()
        escritor.writerows(validos)

    with open(ARQUIVO_PENDENCIAS, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas_pendencias)
        escritor.writeheader()
        escritor.writerows(pendencias)

    situacoes = Counter(aluno["Situação"] for aluno in validos)

    print("\n===== RELATÓRIO DO PROCESSAMENTO =====")
    print(f"Registros lidos: {total}")
    print(f"Registros prontos: {len(validos)}")
    print(f"Registros para revisão: {len(pendencias)}")
    print(f"Aprovados: {situacoes['Aprovado']}")
    print(f"Reprovados: {situacoes['Reprovado']}")
    print(f"\nArquivo criado: {ARQUIVO_VALIDOS.name}")
    print(f"Arquivo criado: {ARQUIVO_PENDENCIAS.name}")
    print("\nAtenção: confira a fórmula de cálculo com a regra oficial.")


if __name__ == "__main__":
    processar()
