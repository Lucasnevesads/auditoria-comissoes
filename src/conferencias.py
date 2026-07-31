"""As conferências da auditoria.

Três blocos, e a ordem importa:

  A. INTEGRIDADE      o que tem que fechar ao centavo. Se não fechar aqui,
                      pare tudo: a base não é confiável e nada depois vale.
  B. A PONTE          explica a diferença entre as duas réguas em vez de
                      acusar. Este é o bloco que separa auditoria de caça
                      às bruxas.
  C. ACHADOS          os erros de preenchimento, um por regra.

Nenhuma função aqui sabe onde estão os erros. Todas partem de uma regra
de negócio e vão procurar quem a viola.
"""

import pandas as pd

TOLERANCIA = 0.01


def _achado(tipo, gravidade, descricao, impacto, apolice="", parcela=""):
    return {
        "tipo": tipo,
        "gravidade": gravidade,
        "numero_apolice": apolice,
        "numero_parcela": parcela,
        "descricao": descricao,
        "impacto_reais": round(float(impacto), 2),
    }


# ---------------------------------------------------------------------------
# BLOCO A · integridade
# ---------------------------------------------------------------------------


def integridade(base):
    """O que precisa fechar ao centavo.

    Banco e seguradora são sistemas: não erram aritmética. Se estas contas
    não baterem, o problema é da extração ou da base, não do controle da
    empresa, e a auditoria tem que parar aqui.
    """
    extrato = base["extrato_bancario"]
    demonstrativos = base["demonstrativos"]
    parcelas = base["parcelas"]

    creditos = extrato.loc[extrato["demonstrativo_id"].notna(), "valor"].sum()
    total_demonstrativos = demonstrativos["valor_total"].sum()
    recebido = parcelas.loc[
        parcelas["status_comissao"] == "Recebido", "valor_comissao"
    ].sum()

    return [
        {
            "conferencia": "Créditos de seguradora no extrato x demonstrativos",
            "esquerda": round(creditos, 2),
            "direita": round(total_demonstrativos, 2),
            "diferenca": round(creditos - total_demonstrativos, 2),
        },
        {
            "conferencia": "Parcelas recebidas x demonstrativos",
            "esquerda": round(recebido, 2),
            "direita": round(total_demonstrativos, 2),
            "diferenca": round(recebido - total_demonstrativos, 2),
        },
    ]


# ---------------------------------------------------------------------------
# BLOCO B · a ponte entre as duas réguas
# ---------------------------------------------------------------------------


def ponte(base):
    """Explica a diferença entre o total do CRM e o dinheiro que entrou.

    O CRM registra a comissão CHEIA na data da venda. O banco recebe PARCELA
    por parcela, conforme o tomador paga o prêmio. Subtrair um do outro
    produz uma diferença que quase nunca é dinheiro faltando.

    Esta função não julga: ela decompõe a diferença em partes com nome, e o
    que sobrar sem nome é o que merece investigação.
    """
    crm = base["crm_negocios"]
    planilha = base["planilha_producao"]

    total_crm = crm["valor_comissao"].sum()
    recebido = planilha.loc[
        planilha["status_comissao"] == "Recebido", "valor_comissao"
    ].sum()

    # 1. Apólices canceladas: estão no CRM como venda, nunca viraram dinheiro.
    canceladas = set(
        planilha.loc[planilha["status_boleto"] == "Cancelado", "numero_apolice"]
    )
    valor_cancelado = crm.loc[
        crm["numero_apolice"].isin(canceladas), "valor_comissao"
    ].sum()

    # 2. Parcelas que ainda não venceram ou não foram pagas.
    #
    # O filtro de boleto cancelado não é detalhe: sem ele, a parcela de uma
    # apólice cancelada que ficou marcada como "Pendente" entra duas vezes,
    # aqui e no item 1, e a ponte subtrai o mesmo dinheiro duas vezes. Foi
    # exatamente o que aconteceu na primeira versão desta função.
    pendente = planilha.loc[
        (planilha["status_comissao"] == "Pendente")
        & (planilha["status_boleto"] != "Cancelado"),
        "valor_comissao",
    ].sum()

    # 3. Negócios do CRM que não têm nenhuma linha na planilha do financeiro.
    com_lastro = set(planilha["numero_apolice"])
    sem_lastro = crm.loc[~crm["numero_apolice"].isin(com_lastro), "valor_comissao"].sum()

    # 4. O que sobra sem explicação. Em auditoria, é isto que importa.
    residuo = total_crm - recebido - valor_cancelado - pendente - sem_lastro

    return {
        "total_crm": round(total_crm, 2),
        "recebido": round(recebido, 2),
        "diferenca": round(total_crm - recebido, 2),
        "componentes": [
            ("Apólices canceladas (venda que nunca virou apólice)", -round(valor_cancelado, 2)),
            ("Parcelas ainda não recebidas (calendário, não atraso)", -round(pendente, 2)),
            ("Negócios sem lastro na planilha do financeiro", -round(sem_lastro, 2)),
            ("Resíduo sem explicação", -round(residuo, 2)),
        ],
        "residuo": round(residuo, 2),
    }


# ---------------------------------------------------------------------------
# BLOCO C · achados
# ---------------------------------------------------------------------------


def competencia_fora_do_mes(base):
    """A aba do mês tem que conter a parcela daquele mês.

    Parcela lançada na aba errada infla um mês e esvazia o outro. Quem
    fecha o mês pela aba acha que produziu o que não produziu.
    """
    planilha = base["planilha_producao"]
    mes_do_vencimento = planilha["data_vencimento"].dt.strftime("%Y-%m")
    erradas = planilha[planilha["competencia_aba"] != mes_do_vencimento]

    return [
        _achado(
            "competencia_trocada",
            "alta",
            f"vencimento em {mes_do_vencimento[i]} lançado na aba "
            f"{linha['competencia_aba']}",
            linha["valor_comissao"],
            linha["numero_apolice"],
            linha["numero_parcela"],
        )
        for i, linha in erradas.iterrows()
    ]


def cancelada_ainda_contando(base):
    """Se o boleto está cancelado, a comissão está cancelada.

    Quando as duas colunas discordam, qualquer fórmula que filtre pela
    coluna errada soma uma apólice que não existe. É o erro que faz a
    diretoria procurar um dinheiro que nunca esteve lá.
    """
    planilha = base["planilha_producao"]
    divergentes = planilha[
        (planilha["status_boleto"] == "Cancelado")
        & (planilha["status_comissao"] != "Cancelado")
    ]

    return [
        _achado(
            "cancelada_como_pendente",
            "alta",
            f"boleto Cancelado mas comissão consta como "
            f"{linha['status_comissao']}",
            linha["valor_comissao"],
            linha["numero_apolice"],
            linha["numero_parcela"],
        )
        for _, linha in divergentes.iterrows()
    ]


def consultor_mal_digitado(base):
    """"Maria " e "Maria" são pessoas diferentes para qualquer fórmula.

    O total geral fecha, o total por vendedor não, e ninguém descobre por
    quê olhando a tela: o espaço é invisível.
    """
    planilha = base["planilha_producao"]
    nome = planilha["consultor"].astype(str)
    sujos = planilha[nome != nome.str.strip()]

    return [
        _achado(
            "consultor_com_espaco",
            "media",
            f"consultor gravado como {linha['consultor']!r}, com espaço sobrando",
            linha["valor_comissao"],
            linha["numero_apolice"],
            linha["numero_parcela"],
        )
        for _, linha in sujos.iterrows()
    ]


def negocio_sem_lastro(base):
    """Negócio fechado no CRM que o financeiro nunca registrou.

    Ou é produção fora de controle, ou é cadastro indevido. Nos dois casos
    costuma ser o item de maior valor unitário de uma auditoria, porque é
    contrato inteiro e não parcela.
    """
    crm = base["crm_negocios"]
    planilha = base["planilha_producao"]
    com_lastro = set(planilha["numero_apolice"])
    orfaos = crm[~crm["numero_apolice"].isin(com_lastro)]

    return [
        _achado(
            "negocio_so_no_crm",
            "alta",
            f"negócio {linha['negocio_id']} ({linha['tomador']}) está no CRM "
            "e não tem nenhuma linha na planilha",
            linha["valor_comissao"],
            linha["numero_apolice"],
        )
        for _, linha in orfaos.iterrows()
    ]


def valor_divergente(base):
    """O valor digitado na planilha tem que ser o valor da parcela.

    A planilha do financeiro não guarda id de sistema, então o casamento é
    pelo par (número da apólice, número da parcela). É o mesmo caminho que
    se faz na mão, e por isso mesmo é onde a digitação aparece.
    """
    planilha = base["planilha_producao"]
    parcelas = base["parcelas"]

    chaves = ["numero_apolice", "numero_parcela"]
    juntas = planilha.merge(
        parcelas[chaves + ["valor_comissao"]],
        on=chaves,
        how="inner",
        suffixes=("_planilha", "_sistema"),
    )
    diferenca = juntas["valor_comissao_planilha"] - juntas["valor_comissao_sistema"]
    divergentes = juntas[diferenca.abs() > TOLERANCIA]

    return [
        _achado(
            "divergencia_de_centavos",
            "baixa",
            f"planilha tem {linha['valor_comissao_planilha']:.2f} e o sistema "
            f"tem {linha['valor_comissao_sistema']:.2f}",
            linha["valor_comissao_planilha"] - linha["valor_comissao_sistema"],
            linha["numero_apolice"],
            linha["numero_parcela"],
        )
        for _, linha in divergentes.iterrows()
    ]


def numero_de_apolice_repetido(base):
    """Duas apólices diferentes com o mesmo número quebram qualquer join.

    Nesta base não deve acontecer. A conferência existe porque, se um dia
    acontecer, todo o resto da auditoria fica errado em silêncio.
    """
    apolices = base["apolices"]
    contagem = apolices["numero_apolice"].value_counts()
    repetidos = contagem[contagem > 1]

    return [
        _achado(
            "numero_apolice_repetido",
            "alta",
            f"o número {numero} aparece em {vezes} apólices diferentes",
            0,
            numero,
        )
        for numero, vezes in repetidos.items()
    ]


CONFERENCIAS = [
    competencia_fora_do_mes,
    cancelada_ainda_contando,
    consultor_mal_digitado,
    negocio_sem_lastro,
    valor_divergente,
    numero_de_apolice_repetido,
]


def rodar_todas(base):
    achados = []
    for conferencia in CONFERENCIAS:
        achados.extend(conferencia(base))
    return pd.DataFrame(achados)
