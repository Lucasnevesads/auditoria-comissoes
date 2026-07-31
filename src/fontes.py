"""Carrega as tabelas que a auditoria tem direito de ler.

A lista está em config/fontes.yml e **não inclui o gabarito**. Isso não é
detalhe de organização: é a regra que dá sentido ao projeto. Se a auditoria
puder ler onde estão os erros, ela não está auditando, está copiando.

A trava é estrutural, não é um comentário pedindo boa vontade: quem chamar
`carregar()` pedindo o gabarito leva uma exceção.
"""

import sys

import pandas as pd

import config

COLUNAS_DE_DATA = {
    "data_emissao",
    "data_fim_vigencia",
    "data_vencimento",
    "data_pagamento",
    "data_criacao",
    "data",
    "cliente_desde",
}


def _caminho(nome):
    return config.PASTA_BASE / f"{nome}.csv"


def carregar(nome):
    if nome == config.NOME_GABARITO:
        raise PermissionError(
            "A auditoria não lê o gabarito. Se ela soubesse onde estão os "
            "erros, não estaria auditando. Quem lê o gabarito é src/medir.py, "
            "depois que a auditoria termina."
        )
    if nome not in config.TABELAS:
        raise KeyError(f"'{nome}' não está na lista de fontes de config/fontes.yml")

    tabela = pd.read_csv(_caminho(nome))
    for coluna in tabela.columns:
        if coluna in COLUNAS_DE_DATA:
            tabela[coluna] = pd.to_datetime(tabela[coluna], errors="coerce")
    return tabela


def carregar_tudo():
    if not config.PASTA_BASE.exists():
        print(
            "Não achei a base em:\n"
            f"  {config.PASTA_BASE}\n\n"
            "A base é gerada por outro projeto. Clone os dois lado a lado:\n\n"
            f"  git clone {config.FONTES['base']['repositorio']}\n"
            "  cd base-sintetica-seguros\n"
            "  pip install -r requirements.txt\n"
            "  python src/gerar_base.py\n\n"
            "Ou ajuste o caminho em config/fontes.yml.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    return {nome: carregar(nome) for nome in config.TABELAS}
