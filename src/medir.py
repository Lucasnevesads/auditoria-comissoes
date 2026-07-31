"""Pontua a auditoria contra o gabarito.

    python src/medir.py

Roda DEPOIS da auditoria, e é o único arquivo do projeto que abre o
gabarito. A separação é o ponto: uma auditoria que consulta a resposta
enquanto trabalha não mede nada.

Duas perguntas:

    achou tudo?          dos erros que existiam, quantos apareceram
    achou só o que há?   dos apontamentos feitos, quantos são erro de verdade
"""

import pandas as pd

import config

CHAVE = ["tipo", "numero_apolice", "numero_parcela"]


def _normalizar(tabela):
    copia = tabela.copy()
    for coluna in CHAVE:
        copia[coluna] = (
            copia[coluna]
            .fillna("")
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )
    return copia


def main():
    caminho_achados = config.PASTA_SAIDA / "achados.csv"
    if not caminho_achados.exists():
        raise SystemExit("Rode 'python src/auditar.py' antes de medir.")

    achados = _normalizar(pd.read_csv(caminho_achados))
    gabarito = _normalizar(
        pd.read_csv(config.PASTA_BASE / f"{config.NOME_GABARITO}.csv")
    )

    chaves_achadas = set(map(tuple, achados[CHAVE].values))
    chaves_reais = set(map(tuple, gabarito[CHAVE].values))

    encontrados = chaves_reais & chaves_achadas
    perdidos = chaves_reais - chaves_achadas
    falsos = chaves_achadas - chaves_reais

    print(f"Gabarito: {len(chaves_reais)} defeitos plantados")
    print(f"Auditoria: {len(chaves_achadas)} apontamentos\n")
    print(f"  Encontrados      {len(encontrados):>3} de {len(chaves_reais)}"
          f"   ({len(encontrados) / len(chaves_reais):.0%})")
    print(f"  Não encontrados  {len(perdidos):>3}")
    print(f"  Falsos positivos {len(falsos):>3}")

    print("\nPor tipo de defeito:")
    print(f"  {'tipo':<28}{'plantados':>10}{'achados':>9}")
    print(f"  {'-' * 47}")
    for tipo, grupo in gabarito.groupby("tipo"):
        chaves_tipo = set(map(tuple, grupo[CHAVE].values))
        print(
            f"  {tipo:<28}{len(chaves_tipo):>10}"
            f"{len(chaves_tipo & chaves_achadas):>9}"
        )

    if perdidos:
        print("\nPassaram batido:")
        for chave in sorted(perdidos):
            print(f"  {chave}")

    if falsos:
        print("\nApontados sem estar no gabarito:")
        for chave in sorted(falsos):
            print(f"  {chave}")
        print(
            "\n  Atenção: falso positivo aqui não é necessariamente erro da\n"
            "  auditoria. Pode ser um efeito colateral de um defeito plantado\n"
            "  que o gabarito não registrou como linha separada."
        )


if __name__ == "__main__":
    main()
