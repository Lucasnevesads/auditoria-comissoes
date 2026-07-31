"""Desenha a imagem do topo do README: a ponte entre as duas réguas.

    python docs/gerar_grafico.py

Não faz parte do produto: é documentação. Por isso o matplotlib está em
requirements-dev.txt e este arquivo vive em docs/ e não em src/.

A forma é uma cascata (waterfall), que é como o mercado financeiro mostra
decomposição de diferença: começa num total, tira as parcelas com nome, e
termina no outro total. Se sobrar altura no fim, sobrou dinheiro sem
explicação.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import conferencias  # noqa: E402
import fontes  # noqa: E402

# Paleta validada com scripts/validate_palette.js da skill de dataviz.
# Claro:  CVD ΔE 24,7 · visão normal 33,6 · contraste >= 3:1
# Escuro: CVD ΔE 26,8 · visão normal 31,8 · contraste >= 3:1
TEMAS = {
    "light": {
        "surface": "#fcfcfb",
        "primaria": "#0b0b0b",
        "secundaria": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "eixo": "#c3c2b7",
        "total": "#2a78d6",
        "reducao": "#eb6834",
    },
    "dark": {
        "surface": "#1a1a19",
        "primaria": "#ffffff",
        "secundaria": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "eixo": "#383835",
        "total": "#3987e5",
        "reducao": "#d95926",
    },
}


def reais(valor):
    sinal = "-" if valor < 0 else ""
    return (
        f"{sinal}R$ {abs(valor):,.2f}"
        .replace(",", "@")
        .replace(".", ",")
        .replace("@", ".")
    )


def montar_passos(ponte):
    """Do total do CRM até o dinheiro que entrou, passo a passo."""
    passos = [("Registrado\nno CRM", ponte["total_crm"], "total")]
    rotulos = {
        "Apólices canceladas (venda que nunca virou apólice)": "Apólices\ncanceladas",
        "Parcelas ainda não recebidas (calendário, não atraso)": "Parcelas ainda\nnão recebidas",
        "Negócios sem lastro na planilha do financeiro": "Negócios sem\nlastro na planilha",
        "Resíduo sem explicação": "Resíduo sem\nexplicação",
    }
    for nome, valor in ponte["componentes"]:
        passos.append((rotulos[nome], valor, "reducao"))
    passos.append(("Recebido\nno banco", ponte["recebido"], "total"))
    return passos


def desenhar(tema_nome, ponte):
    t = TEMAS[tema_nome]
    passos = montar_passos(ponte)

    figura, eixo = plt.subplots(figsize=(11, 5.4), dpi=170)
    figura.patch.set_facecolor(t["surface"])
    eixo.set_facecolor(t["surface"])

    # Calcula onde cada barra começa e termina ANTES de desenhar. Cascata
    # feita direto no laço de desenho vira código impossível de conferir.
    barras = []      # (base, altura) de cada barra
    niveis = []      # o nível corrente depois de cada passo
    corrente = 0.0
    for _, valor, papel in passos:
        if papel == "total":
            barras.append((0.0, valor))
            corrente = valor
        else:
            novo = corrente + valor          # valor é negativo
            barras.append((novo, corrente - novo))
            corrente = novo
        niveis.append(corrente)

    for posicao, ((base, altura), (_, valor, papel)) in enumerate(
        zip(barras, passos)
    ):
        eixo.bar(posicao, altura, bottom=base, width=0.62, color=t[papel], zorder=3)

        # Linha fina ligando um passo ao próximo. É ela que faz a cascata
        # ser lida como uma conta em vez de seis barras soltas.
        if posicao < len(passos) - 1:
            eixo.plot(
                [posicao + 0.31, posicao + 1 - 0.31],
                [niveis[posicao], niveis[posicao]],
                color=t["eixo"],
                linewidth=1,
                linestyle=(0, (3, 3)),
                zorder=2,
            )

        # Valor escrito acima da barra, em cor de texto e não de série.
        eixo.text(
            posicao,
            base + altura + ponte["total_crm"] * 0.02,
            reais(valor),
            ha="center",
            va="bottom",
            color=t["primaria"],
            fontsize=9.5,
            fontweight="bold",
        )

    eixo.set_title(
        "A diferença de R$ 630 mil está inteiramente explicada",
        color=t["primaria"],
        fontsize=15,
        loc="left",
        pad=34,
        fontweight="bold",
    )
    eixo.text(
        0,
        1.045,
        "Norte Garantia · 2025 · do total do CRM até o dinheiro que entrou · base sintética",
        transform=eixo.transAxes,
        color=t["secundaria"],
        fontsize=10,
    )

    eixo.set_xticks(range(len(passos)))
    eixo.set_xticklabels([p[0] for p in passos])
    eixo.set_ylim(0, ponte["total_crm"] * 1.18)
    eixo.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(
            lambda v, _: "0" if v == 0 else f"R$ {v / 1_000_000:.1f} mi".replace(".", ",")
        )
    )

    eixo.grid(axis="y", color=t["grid"], linewidth=0.8)
    eixo.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        eixo.spines[lado].set_visible(False)
    eixo.spines["bottom"].set_color(t["eixo"])
    eixo.tick_params(colors=t["muted"], labelsize=9, length=0)
    eixo.tick_params(axis="x", labelsize=9.5, colors=t["secundaria"])

    figura.tight_layout()
    saida = RAIZ / "docs" / f"grafico-{tema_nome}.png"
    figura.savefig(saida, facecolor=t["surface"], bbox_inches="tight")
    plt.close(figura)
    return saida


def main():
    base = fontes.carregar_tudo()
    p = conferencias.ponte(base)
    for tema in TEMAS:
        print("gerado:", desenhar(tema, p))


if __name__ == "__main__":
    main()
