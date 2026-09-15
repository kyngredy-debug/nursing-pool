#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_sankey.py
===============
Gera um diagrama de Sankey (fluxo metodológico) em PORTUGUÊS para a seção
de Metodologia do trabalho.

O diagrama representa a cadeia de derivação da camada NANDA-I / NOC / NIC
a partir do MIMIC-IV Demo v2.2, com os números reais congelados do projeto.

Saída: output/figures/Sankey_Metodologia.png (alta resolução, 200+ dpi).

Uso:
    python gerar_sankey.py
"""

import os
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "output", "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def br(n):
    """Formato brasileiro: 20.566."""
    return f"{int(round(n)):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Nós do Sankey (com contagens reais do projeto)
# ---------------------------------------------------------------------------
labels = [
    # Coluna 0 — Evidências por método de inferência
    f"Limiar clínico operacional<br>({br(20566)})",
    f"Palavra-chave clínica<br>({br(2644)})",
    f"Fallback Transformer biomédico<br>({br(1862)})",

    # Coluna 0 — Fontes dos proxies NIC (ramo independente)
    f"Administrações (eMAR)<br>({br(34829)})",
    f"Insumos intravenosos (inputevents)<br>({br(20404)})",

    # Coluna 1 — Categoria de evidência
    f"Característica definidora operacional<br>({br(20566)})",
    f"Condição associada<br>({br(4506)})",

    # Coluna 2 — Hipóteses NANDA-I
    f"Hipóteses NANDA-I<br>({br(1629)})",

    # Coluna 3 — Status da hipótese
    f"Suportada por regra<br>({br(1204)})",
    f"Candidata<br>({br(425)})",

    # Coluna 4 — Saídas da camada NOC / NIC
    f"Indicadores NOC<br>({br(685)})",
    f"Recomendações NIC (regras NNN)<br>({br(1365)})",
    f"Proxies NIC observáveis<br>({br(55233)})",
]

# Índices (posição em `labels`)
LIMIAR, PALAVRA, TRANSFORMER = 0, 1, 2
EMAR, INPUTEVENTS = 3, 4
CARACTERISTICA, CONDICAO = 5, 6
HIPOTESES = 7
SUPORTADA, CANDIDATA = 8, 9
NOC, RECOMENDACOES, PROXIES = 10, 11, 12

# Posição horizontal de cada nó (0 = esquerda, 1 = direita)
x_pos = [
    0.00, 0.00, 0.00,          # métodos
    0.00, 0.00,                # fontes dos proxies (mesma coluna, base)
    0.32, 0.32,                # categorias
    0.58,                      # hipóteses
    0.78, 0.78,                # status
    0.98, 0.98, 0.98,          # saídas
]

# Cores dos nós por estágio
node_colors = [
    "#1F77B4", "#1F77B4", "#1F77B4",   # métodos (azul)
    "#FF7F0E", "#FF7F0E",              # fontes dos proxies (laranja)
    "#6BAED6", "#6BAED6",              # categorias (azul claro)
    "#2CA02C",                         # hipóteses (verde)
    "#2CA02C", "#999999",              # status (verde / cinza)
    "#D62728", "#9467BD", "#FF7F0E",   # saídas (vermelho / roxo / laranja)
]

# ---------------------------------------------------------------------------
# Ligações (source, target, value)
# ---------------------------------------------------------------------------
links = dict(
    source=[
        LIMIAR, PALAVRA, TRANSFORMER,      # métodos -> categorias
        EMAR, INPUTEVENTS,                 # fontes -> proxies NIC
        CARACTERISTICA, CONDICAO,          # categorias -> hipóteses
        HIPOTESES, HIPOTESES,              # hipóteses -> status
        SUPORTADA, SUPORTADA,              # status -> saídas
    ],
    target=[
        CARACTERISTICA, CONDICAO, CONDICAO,
        PROXIES, PROXIES,
        HIPOTESES, HIPOTESES,
        SUPORTADA, CANDIDATA,
        NOC, RECOMENDACOES,
    ],
    value=[
        20566, 2644, 1862,
        34829, 20404,
        20566, 4506,
        1204, 425,
        685, 1365,
    ],
)

# Cores das ligações (tom do nó de origem, com transparência)
link_colors = [
    "rgba(31,119,180,0.30)", "rgba(31,119,180,0.30)", "rgba(31,119,180,0.30)",
    "rgba(255,127,14,0.30)", "rgba(255,127,14,0.30)",
    "rgba(44,160,44,0.28)",  "rgba(44,160,44,0.28)",
    "rgba(44,160,44,0.32)",  "rgba(153,153,153,0.38)",
    "rgba(214,39,40,0.32)",  "rgba(148,103,189,0.32)",
]

# ---------------------------------------------------------------------------
# Construção do Sankey
# ---------------------------------------------------------------------------
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=18,
        thickness=26,
        line=dict(color="#333333", width=0.6),
        label=labels,
        color=node_colors,
        x=x_pos,
        hovertemplate="%{label}<extra></extra>",
    ),
    link=dict(
        source=links["source"],
        target=links["target"],
        value=links["value"],
        color=link_colors,
        hovertemplate="Fluxo: %{value:,} registros<extra></extra>",
    ),
)])

fig.update_layout(
    title=dict(
        text=("Fluxo Metodológico — Derivação da Camada NANDA-I / NOC / NIC<br>"
              "<sup>MIMIC-IV Demo v2.2 (prova de conceito) — números congelados do projeto</sup>"),
        font=dict(size=26, color="#222222"),
        x=0.01,
        xanchor="left",
    ),
    font=dict(family="Arial, sans-serif", size=15, color="#222222"),
    width=1900,
    height=950,
    margin=dict(l=10, r=10, t=110, b=60),
    paper_bgcolor="white",
)

# Anotações de rodapé (notas metodológicas)
fig.add_annotation(
    x=0.01, y=-0.06, xref="paper", yref="paper",
    showarrow=False, align="left",
    font=dict(size=13, color="#777777"),
    text=("Nota: 25.072 evidências são agregadas em 1.629 hipóteses NANDA-I "
          "(redução média de ~15 evidências por hipótese). "
          "Indicadores NOC e recomendações NIC derivam apenas de hipóteses suportadas por regra. "
          "Proxies NIC vêm de eventos registrados (eMAR/insumos IV), não de hipóteses."),
)

# ---------------------------------------------------------------------------
# Exportação
# ---------------------------------------------------------------------------
png_path = os.path.join(FIG_DIR, "Sankey_Metodologia.png")
fig.write_image(png_path, width=1900, height=950, scale=2)  # 3800x1900 px
print(f"[OK] Sankey salvo em: {png_path}")
