#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analises_demonstracao.py
========================
Análises demonstrativas do VALOR de um banco de dados integrado
NANDA-I / NOC / NIC (camada derivada do MIMIC-IV Demo v2.2).

Demonstra ao público as possibilidades de análise que uma base
terminológica de enfermagem estruturada viabiliza:

    1. Rastreamento de desfechos NOC (admissão vs. follow-up)
    2. Vínculo NANDA -> NOC (diagnóstico -> resultado mensurável)
    3. Vínculo NANDA -> NIC (diagnóstico -> intervenção)
    4. Carga diagnóstica -> desfechos (LOS, mortalidade)
    5. Cadeia NNN completa (diagnóstico -> resultado -> intervenção)

Saídas:
    output/figures/FigA_*.png ... FigG_*.png
    output/ANALISES_DEMONSTRACAO.md

Uso:
    python analises_demonstracao.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "output", "figures")
OUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Tipografia GRANDE para slides
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 16,
    "axes.titlesize": 20,
    "axes.titleweight": "bold",
    "axes.labelsize": 17,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 13,
    "axes.labelweight": "bold",
    "figure.dpi": 110,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 1.1,
    "axes.grid": True,
    "grid.color": "#D9D9D9",
    "grid.linewidth": 0.8,
    "grid.alpha": 0.7,
})

C = {
    "azul": "#1F77B4", "verde": "#2CA02C", "vermelho": "#D62728",
    "laranja": "#FF7F0E", "roxo": "#9467BD", "cinza": "#7F7F7F",
    "marrom": "#8C564B",
}


def salvar(fig, nome):
    fig.savefig(os.path.join(FIG_DIR, nome + ".png"),
                bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  [OK] {nome}.png")


def br(n):
    return f"{int(round(n)):,}".replace(",", ".")


def fmt_br(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------
hyp = pd.read_csv(os.path.join(DATA_DIR, "fact_nanda_hypothesis.csv"))
noc = pd.read_csv(os.path.join(DATA_DIR, "fact_noc_measurement.csv"))
rec = pd.read_csv(os.path.join(DATA_DIR, "fact_nic_recommended.csv"))
adm = pd.read_csv(os.path.join(DATA_DIR, "admissions.csv"))
icu = pd.read_csv(os.path.join(DATA_DIR, "icustays.csv"))

# Sanitização: SpO2 limitada a 0-100%
noc = noc.copy()
mask_spo2 = noc["indicator"] == "SpO2"
noc.loc[mask_spo2, "baseline_value"] = noc.loc[mask_spo2, "baseline_value"].clip(0, 100)
noc.loc[mask_spo2, "followup_value"] = noc.loc[mask_spo2, "followup_value"].clip(0, 100)

IND_NOME = {
    "SpO2": "SpO₂ (%)",
    "FC": "Frequência cardíaca (bpm)",
    "PA Sistolica": "PA sistólica (mmHg)",
    "GCS": "Escala de Coma de Glasgow",
    "Temperatura": "Temperatura (°F)",
    "Dor NRS": "Dor (NRS 0-10)",
}

DOM = {
    "Atividade/Repouso": "Atividade/Repouso",
    "Seguranca/Protecao": "Segurança/Proteção",
    "Nutricao": "Nutrição",
    "Eliminacao e Troca": "Eliminação e Troca",
    "Percepcao/Cognicao": "Percepção/Cognição",
    "Enfrentamento/Tolerancia ao Estresse": "Enfrentamento/Tolerância ao Estresse",
    "Conforto": "Conforto",
    "Autopercepcao": "Autopercepção",
    "Sexualidade": "Sexualidade",
    "Promocao da Saude": "Promoção da Saúde",
    "Crescimento/Desenvolvimento": "Crescimento/Desenvolvimento",
    "Papeis e Relacionamentos": "Papéis e Relacionamentos",
    "Principios Vitais": "Princípios Vitais",
}


# ===========================================================================
# FIGURA A — Rastreamento de desfechos NOC (admissão vs. follow-up)
# ===========================================================================
print("FigA: Rastreamento de desfechos NOC...")
indicadores = ["SpO2", "FC", "PA Sistolica", "GCS", "Temperatura", "Dor NRS"]
fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
for ax, ind in zip(axes.flat, indicadores):
    g = noc[noc["indicator"] == ind]
    base = g["baseline_value"].median()
    fol = g["followup_value"].median()
    ax.plot([0, 1], [base, fol], color="#555555", linewidth=2.5, zorder=2)
    ax.scatter([0, 1], [base, fol], s=220,
               color=[C["azul"], C["verde"]], zorder=3, edgecolor="white", linewidth=1.5)
    ax.annotate("", xy=(1, fol), xytext=(0, base),
                arrowprops=dict(arrowstyle="-|>", color="#555555", lw=2.5))
    delta = fol - base
    ax.text(0.5, max(base, fol) + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.04,
            f"Δ {fmt_br(delta, 1)}", ha="center", fontsize=15,
            fontweight="bold",
            color=C["verde"] if delta > 0 else (C["vermelho"] if delta < 0 else "#555555"))
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Admissão", "Follow-up"])
    ax.set_title(IND_NOME[ind], pad=10, fontsize=16)
    ax.grid(axis="x", visible=False)
    ax.margins(y=0.25)

fig.suptitle("Rastreamento de Desfechos NOC — mediana na Admissão vs. Follow-up",
             fontsize=22, fontweight="bold", y=1.00)
fig.text(0.01, 0.005,
         "Cada painel = um indicador de resultado (NOC) medido em dois momentos. "
         "Valores em unidades nativas do MIMIC-IV.",
         fontsize=13, color="#777777")
salvar(fig, "FigA_NOC_Evolucao")

# ===========================================================================
# FIGURA B — Percentual de pacientes que melhoraram por indicador
# ===========================================================================
print("FigB: Melhoria por indicador NOC...")
melhoria = {}
for ind, grp in noc.groupby("indicator"):
    d = grp["followup_value"] - grp["baseline_value"]
    if ind in ("SpO2", "GCS"):
        melhor = (d > 0).sum()
    elif ind == "Dor NRS":
        melhor = (d < 0).sum()
    elif ind == "FC":
        melhor = (np.abs(grp["followup_value"] - 80) < np.abs(grp["baseline_value"] - 80)).sum()
    elif ind == "PA Sistolica":
        melhor = (np.abs(grp["followup_value"] - 115) < np.abs(grp["baseline_value"] - 115)).sum()
    else:  # Temperatura -> 98.6 °F
        melhor = (np.abs(grp["followup_value"] - 98.6) < np.abs(grp["baseline_value"] - 98.6)).sum()
    melhoria[IND_NOME[ind]] = 100 * melhor / len(grp)

serie = pd.Series(melhoria).sort_values()
fig, ax = plt.subplots(figsize=(12, 6.5))
bars = ax.barh(serie.index, serie.values, color=C["verde"], height=0.6, alpha=0.9)
for b, v in zip(bars, serie.values):
    ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
            f"{fmt_br(v, 0)}%", va="center", ha="left",
            fontsize=16, fontweight="bold", color="#222222")
ax.set_xlabel("% de pacientes que melhoraram")
ax.set_title("Proporção de Pacientes com Melhora no Desfecho (NOC)",
             pad=18, loc="left")
ax.set_xlim(0, 100)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         "Melhora avaliada por direção clínica esperada (ex.: ↑ SpO₂, ↓ dor, → normalização de FC/PA/temperatura).",
         fontsize=12, color="#777777")
salvar(fig, "FigB_NOC_Melhoria")

# ===========================================================================
# FIGURA C — Vínculo NANDA -> NOC (medições por domínio)
# ===========================================================================
print("FigC: Vínculo NANDA -> NOC...")
noc_dom = noc.merge(hyp[["hypothesis_id", "nanda_domain"]], on="hypothesis_id")
cC = noc_dom.groupby("nanda_domain")["noc_measurement_id"].count().sort_values()
cC.index = [DOM.get(d, d) for d in cC.index]
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(cC.index, cC.values, color=C["azul"], height=0.6, alpha=0.9)
for b, v in zip(bars, cC.values):
    ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Nº de medições NOC vinculadas")
ax.set_title("Diagnósticos NANDA-I Vinculados a Resultados NOC Mensuráveis",
             pad=18, loc="left")
ax.set_xlim(0, cC.max() * 1.2)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         "Cada hipótese NANDA-I pode ser ligada a indicadores NOC observáveis (ex.: Atividade/Repouso → SpO₂, FC, PA).",
         fontsize=12, color="#777777")
salvar(fig, "FigC_NANDA_NOC")

# ===========================================================================
# FIGURA D — Vínculo NANDA -> NIC (recomendações por domínio)
# ===========================================================================
print("FigD: Vínculo NANDA -> NIC...")
cD = rec.groupby("nanda_domain")["recommendation_id"].count().sort_values()
cD.index = [DOM.get(d, d) for d in cD.index]
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(cD.index, cD.values, color=C["laranja"], height=0.6, alpha=0.9)
for b, v in zip(bars, cD.values):
    ax.text(b.get_width() + 4, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Nº de recomendações NIC derivadas")
ax.set_title("Diagnósticos NANDA-I Vinculados a Intervenções NIC (regras NNN)",
             pad=18, loc="left")
ax.set_xlim(0, cD.max() * 1.18)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         "1.365 recomendações NIC geradas automaticamente por 7 regras de ligação NANDA-NOC-NIC.",
         fontsize=12, color="#777777")
salvar(fig, "FigD_NANDA_NIC")

# ===========================================================================
# FIGURA E — Carga diagnóstica NANDA vs. tempo de internação em UTI
# ===========================================================================
print("FigE: Carga diagnóstica vs LOS...")
carga = hyp.groupby("subject_id")["hypothesis_id"].count().reset_index(name="n_hip")
icu2 = icu.groupby("subject_id")["los"].sum().reset_index(name="los_uti")
df = carga.merge(icu2, on="subject_id", how="inner")
r, p = stats.spearmanr(df["n_hip"], df["los_uti"])

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.scatter(df["n_hip"], df["los_uti"], s=70, alpha=0.55,
           color=C["azul"], edgecolor="white", linewidth=0.8)
z = np.polyfit(df["n_hip"], df["los_uti"], 1)
xlin = np.linspace(df["n_hip"].min(), df["n_hip"].max(), 100)
ax.plot(xlin, np.polyval(z, xlin), color=C["vermelho"], linewidth=2.5,
        label="Tendência linear")
ax.set_xlabel("Nº de hipóteses NANDA-I por paciente")
ax.set_ylabel("Tempo total de UTI (dias)")
ax.set_title("Quanto Mais Diagnósticos NANDA-I, Maior o Tempo de UTI",
             pad=18, loc="left")
ax.text(0.03, 0.92, f"ρ de Spearman = {r:.2f}   (p = {p:.3f})",
        transform=ax.transAxes, fontsize=15, fontweight="bold",
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC"))
ax.legend(loc="lower right", frameon=False, fontsize=13)
fig.text(0.01, -0.02,
         "Cada ponto = 1 paciente (n=100). Associação positiva moderada: maior carga diagnóstica → maior permanência em UTI.",
         fontsize=12, color="#777777")
salvar(fig, "FigE_Carga_LOS")

# ===========================================================================
# FIGURA F — Carga diagnóstica vs. desfecho (mortalidade e LOS)
# ===========================================================================
print("FigF: Carga diagnóstica vs desfecho...")
adm2 = adm.groupby("subject_id")["hospital_expire_flag"].max().reset_index(name="obito")
df2 = carga.merge(adm2, on="subject_id").merge(icu2, on="subject_id", how="left")
med = df2["n_hip"].median()
df2["grupo"] = np.where(df2["n_hip"] > med, "Alta carga\n(> mediana)", "Baixa carga\n(≤ mediana)")
resumo = df2.groupby("grupo").agg(
    mortalidade=("obito", "mean"),
    los_medi=("los_uti", "median"),
    n=("subject_id", "count"),
).reindex(["Baixa carga\n(≤ mediana)", "Alta carga\n(> mediana)"])

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
# Mortalidade
bars = axes[0].bar(resumo.index, resumo["mortalidade"] * 100,
                    color=[C["verde"], C["vermelho"]], width=0.55, alpha=0.9)
for b, v in zip(bars, resumo["mortalidade"] * 100):
    axes[0].text(b.get_x() + b.get_width() / 2, b.get_height() + 1,
                 f"{fmt_br(v, 1)}%", ha="center", va="bottom",
                 fontsize=18, fontweight="bold", color="#222222")
axes[0].set_ylabel("Mortalidade hospitalar (%)")
axes[0].set_title("Mortalidade por Carga Diagnóstica", pad=12)
axes[0].set_ylim(0, 35)
axes[0].grid(axis="x", visible=False)
# LOS
bars = axes[1].bar(resumo.index, resumo["los_medi"],
                   color=[C["verde"], C["vermelho"]], width=0.55, alpha=0.9)
for b, v in zip(bars, resumo["los_medi"]):
    axes[1].text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15,
                 f"{fmt_br(v, 1)} dias", ha="center", va="bottom",
                 fontsize=18, fontweight="bold", color="#222222")
axes[1].set_ylabel("Mediana do tempo de UTI (dias)")
axes[1].set_title("Permanência em UTI por Carga Diagnóstica", pad=12)
axes[1].set_ylim(0, 7)
axes[1].grid(axis="x", visible=False)
fig.suptitle("Carga de Diagnósticos NANDA-I e Desfechos Clínicos",
             fontsize=21, fontweight="bold")
fig.text(0.01, -0.02,
         f"Divisão pela mediana de hipóteses por paciente ({med:.0f}). "
         "Alta carga diagnóstica → mortalidade 3,1× maior e permanência em UTI 2,5× maior.",
         fontsize=12, color="#777777")
salvar(fig, "FigF_Carga_Desfecho")

# ===========================================================================
# FIGURA G — Cadeia NNN completa (exemplo: Atividade/Repouso)
# ===========================================================================
print("FigG: Cadeia NNN...")
fig, ax = plt.subplots(figsize=(15, 5.5))
ax.axis("off")

def caixa(x, y, w, h, titulo, linhas, cor):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02",
                                fc=cor, ec="none", alpha=0.92))
    ax.text(x + w / 2, y + h * 0.80, titulo, ha="center", va="center",
            fontsize=17, fontweight="bold", color="white")
    n = len(linhas)
    topo = y + h * 0.52
    base = y + h * 0.06
    espaco = (topo - base) / max(n - 1, 1)
    for i, lin in enumerate(linhas):
        ax.text(x + w / 2, topo - i * espaco, lin, ha="center",
                va="center", fontsize=13, color="white")

def seta(x1, y1, x2, y2, cor="#555555"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle="-|>", mutation_scale=22,
                                 linewidth=2.5, color=cor))

# Diagnóstico
caixa(0.02, 0.30, 0.24, 0.40, "DIAGNÓSTICO (NANDA-I)",
      ["Domínio: Atividade/Repouso", "256 hipóteses", "Intolerância à atividade,",
       "padrão respiratório ineficaz"], C["vermelho"])
# Resultados
caixa(0.40, 0.12, 0.24, 0.76, "RESULTADOS (NOC)",
      ["SpO₂ — 127 medições", "Frequência cardíaca — 127", "PA sistólica — 127",
       "(381 medições vinculadas)"], C["azul"])
# Intervenções
caixa(0.78, 0.30, 0.20, 0.40, "INTERVENÇÕES (NIC)",
      ["Oxigenoterapia — 249", "Cuidados cardíacos — 249",
       "(498 recomendações)"], C["verde"])
seta(0.27, 0.50, 0.39, 0.50)
seta(0.65, 0.50, 0.77, 0.50)
ax.text(0.33, 0.57, "vínculo", ha="center", fontsize=12, color="#555555", style="italic")
ax.text(0.71, 0.57, "regras NNN", ha="center", fontsize=12, color="#555555", style="italic")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title("Cadeia NNN Completa — exemplo do domínio Atividade/Repouso",
             fontsize=21, fontweight="bold", pad=15)
fig.text(0.01, 0.02,
         "Com NANDA-NOC-NIC integrados, é possível percorrer a cadeia completa: "
         "diagnóstico → resultado mensurável → intervenção recomendada.",
         fontsize=12, color="#777777")
salvar(fig, "FigG_NNN_Cadeia")

# ===========================================================================
# Relatório em markdown
# ===========================================================================
print("Gerando relatório...")
r_s, p_s = stats.spearmanr(df["n_hip"], df["los_uti"])
rel = f"""# Análises Demonstrativas — Banco NANDA-I / NOC / NIC

**Objetivo:** demonstrar o valor de uma base de dados de enfermagem integrada
(diagnósticos NANDA-I + resultados NOC + intervenções NIC) para a análise de
desfechos e processos assistenciais.

> Camada derivada do MIMIC-IV Demo v2.2 — prova de conceito, não validada
> clinicamente. Números congelados do projeto.

## 1. Rastreamento de desfechos (NOC)

Com a base integrada, cada hipótese diagnóstica é vinculada a **indicadores de
resultado mensuráveis**, com valor na admissão e no follow-up.

| Indicador NOC | Admissão (mediana) | Follow-up (mediana) | Δ | Pacientes que melhoraram |
|---|---|---|---|---|
| SpO₂ (%) | 98,0 | 100,0 | +2,0 | 40% |
| Frequência cardíaca (bpm) | 95,0 | 96,0 | +1,0 | 54% |
| PA sistólica (mmHg) | 93,0 | 95,0 | +2,0 | 54% |
| Escala de Coma de Glasgow | 5,0 | 5,0 | 0,0 | 25% |
| Temperatura (°F) | 98,3 | 98,2 | −0,1 | 39% |
| Dor (NRS 0-10) | 6,0 | 6,0 | 0,0 | 10% |

**Leitura:** a base permite *quantificar* a evolução dos desfechos de
enfermagem ao longo da internação — algo inviável sem terminologia NOC.

## 2. Vínculo diagnóstico → resultado (NANDA → NOC)

- **431 de 1.629 hipóteses** (26%) possuem indicador NOC vinculado —
  todas *suportadas por regra* (431/1.204 = 36%).
- Domínio com mais resultados monitorados: **Atividade/Repouso** (381 medições),
  seguido de Percepção/Cognição (128) e Segurança/Proteção (127).

## 3. Vínculo diagnóstico → intervenção (NANDA → NIC)

- **1.365 recomendações NIC** geradas automaticamente (0,84 por hipótese) por
  **7 regras de ligação NNN** (Moorhead et al., 2024).
- Principais domínios: Atividade/Repouso (498), Segurança/Proteção (201),
  Nutrição (197), Eliminação e Troca (179).

## 4. Carga diagnóstica e desfechos clínicos

| Grupo (carga NANDA-I) | n | Mortalidade | Mediana LOS-UTI |
|---|---|---|---|
| Baixa carga (≤ mediana) | 53 | **7,5%** | **1,94 dias** |
| Alta carga (> mediana) | 47 | **23,4%** | **4,91 dias** |

- Correlação de Spearman entre nº de hipóteses NANDA-I e tempo de UTI:
  **ρ = {r_s:.2f}** (p = {p_s:.3f}).
- Alta carga diagnóstica → **mortalidade 3,1× maior** e **permanência em UTI
  2,5× maior**.

## 5. Cadeia NNN completa (exemplo)

Atividade/Repouso → **NOC** (SpO₂, FC, PA sistólica) → **NIC**
(Oxigenoterapia 249, Cuidados Cardíacos 249). A integração permite percorrer
toda a cadeia *diagnóstico → resultado → intervenção*.

## Conclusão

Um banco NANDA-NOC-NIC estruturado viabiliza:

1. **medir desfechos** sensíveis à enfermagem (baseline vs. follow-up);
2. **rastrear a cadeia** diagnóstico → resultado → intervenção;
3. **auditar o processo** (intervenções recomendadas vs. realizadas);
4. **analisar associações** entre carga diagnóstica e desfechos (LOS,
   mortalidade);
5. **identificar lacunas** (ex.: apenas 36% das hipóteses suportadas têm
   desfecho NOC medido).

---
*Prova de conceito — as associações são exploratórias e NÃO validam relação
causal nem utilidade clínica.*
"""

with open(os.path.join(OUT_DIR, "ANALISES_DEMONSTRACAO.md"), "w",
          encoding="utf-8") as fh:
    fh.write(rel)
print(f"  [OK] output/ANALISES_DEMONSTRACAO.md")

print("\nAnálises demonstrativas concluídas.")
print(f"Figuras: {FIG_DIR}")
print(f"Relatório: {os.path.join(OUT_DIR, 'ANALISES_DEMONSTRACAO.md')}")
