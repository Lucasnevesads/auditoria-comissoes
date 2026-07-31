"""Roda a auditoria e emite o relatório.

    python src/auditar.py

Este arquivo não conhece o gabarito. Ele parte das regras de negócio e vai
procurar quem as viola, do mesmo jeito que se faz quando ninguém sabe onde
estão os erros, que é sempre.
"""

import config
import conferencias
import fontes

LARGURA = 74


def reais(valor):
    """R$ 1.234.567,89 no formato brasileiro."""
    sinal = "-" if valor < 0 else ""
    return (
        f"{sinal}R$ {abs(valor):,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
    )


def _titulo(texto):
    return f"\n{texto}\n{'=' * min(len(texto), LARGURA)}"


def montar_relatorio(base):
    linhas = []
    escrever = linhas.append

    escrever(f"# Auditoria de comissões · {config.EMPRESA['nome']}")
    escrever("")
    escrever(
        f"{len(base['apolices'])} apólices · "
        f"{len(base['parcelas'])} parcelas · "
        f"{len(base['planilha_producao'])} linhas na planilha do financeiro"
    )

    # --- Bloco A ---
    escrever(_titulo("1. Integridade das fontes"))
    escrever("")
    escrever("O que precisa fechar ao centavo. Se falhar aqui, nada abaixo vale.")
    escrever("")
    integro = True
    for item in conferencias.integridade(base):
        ok = abs(item["diferenca"]) < conferencias.TOLERANCIA
        integro = integro and ok
        escrever(f"  [{'OK' if ok else 'FALHOU'}] {item['conferencia']}")
        escrever(
            f"         {reais(item['esquerda'])} x {reais(item['direita'])}  "
            f"diferença {reais(item['diferenca'])}"
        )
    escrever("")
    escrever(
        "As duas fecham. Banco e seguradora são sistemas e não erram conta:"
        if integro
        else "ALGUMA CONFERÊNCIA DE INTEGRIDADE FALHOU. Pare e revise a extração."
    )
    if integro:
        escrever("qualquer divergência daqui pra frente vem do controle manual.")

    # --- Bloco B ---
    p = conferencias.ponte(base)
    escrever(_titulo("2. A diferença entre as duas réguas"))
    escrever("")
    escrever(f"  Registrado no CRM (comissão cheia, data da venda)  {reais(p['total_crm']):>18}")
    escrever(f"  Recebido no banco (parcela, data do pagamento)     {reais(p['recebido']):>18}")
    escrever(f"  {'-' * 68}")
    escrever(f"  Diferença                                          {reais(p['diferenca']):>18}")
    escrever("")
    escrever("Decompondo a diferença:")
    escrever("")
    for nome, valor in p["componentes"]:
        escrever(f"  {nome:<52}{reais(valor):>16}")
    escrever("")
    if abs(p["residuo"]) < 1:
        escrever(
            "A diferença está inteiramente explicada. Não é dinheiro faltando:"
        )
        escrever(
            "é venda cancelada, parcela que ainda não venceu e negócio que o"
        )
        escrever("financeiro não recebeu. Nenhum real sem destino.")
    else:
        escrever(
            f"Sobrou {reais(p['residuo'])} sem explicação. É por aqui que se começa."
        )

    # --- Bloco C ---
    achados = conferencias.rodar_todas(base)
    escrever(_titulo("3. Achados"))
    escrever("")
    if achados.empty:
        escrever("  Nenhum achado.")
    else:
        resumo = (
            achados.groupby(["gravidade", "tipo"])
            .agg(quantidade=("tipo", "size"), impacto=("impacto_reais", lambda s: s.abs().sum()))
            .reset_index()
            .sort_values(["gravidade", "impacto"], ascending=[True, False])
        )
        escrever(f"  {'gravidade':<12}{'tipo':<28}{'qtd':>5}{'impacto':>18}")
        escrever(f"  {'-' * 63}")
        for _, linha in resumo.iterrows():
            escrever(
                f"  {linha['gravidade']:<12}{linha['tipo']:<28}"
                f"{linha['quantidade']:>5}{reais(linha['impacto']):>18}"
            )
        escrever(f"  {'-' * 63}")
        escrever(
            f"  {'TOTAL':<40}{len(achados):>5}"
            f"{reais(achados['impacto_reais'].abs().sum()):>18}"
        )

    escrever("")
    escrever("Detalhe linha a linha em saida/achados.csv")
    return "\n".join(linhas), achados


def main():
    base = fontes.carregar_tudo()
    relatorio, achados = montar_relatorio(base)

    config.PASTA_SAIDA.mkdir(exist_ok=True)
    (config.PASTA_SAIDA / "relatorio.md").write_text(relatorio, encoding="utf-8")
    achados.to_csv(config.PASTA_SAIDA / "achados.csv", index=False, encoding="utf-8")

    print(relatorio)
    print(f"\nRelatório salvo em {config.PASTA_SAIDA / 'relatorio.md'}")
    print("Para pontuar a auditoria contra o gabarito: python src/medir.py")


if __name__ == "__main__":
    main()
