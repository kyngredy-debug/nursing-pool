#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_figuras_slides.py
=======================
Gera TODAS as figuras do projeto (output/figures) em PORTUGUÊS, com
acentuação correta e fontes GRANDES, otimizadas para apresentação de slides.

As figuras são salvas APENAS em PNG (alta resolução, 200 dpi).

Fonte dos dados: arquivos CSV versionados em data/ (export do banco de
enfermagem derivado, MIMIC-IV Demo v2.2).

Conjunto de figuras:
    Fig1  .. Fig5   — resultados da camada derivada NANDA-I / NOC / NIC
    Fig6  .. Fig7   — distribuição do banco de dados
    Fig8  .. Fig16  — perfil dos pacientes
    Fig17 .. Fig22  — aspectos do método de inferência

Uso:
    python gerar_figuras_slides.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------------------------
# Configuração de caminhos
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "output", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Tipografia GRANDE para slides
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 17,
    "axes.titlesize": 22,
    "axes.titleweight": "bold",
    "axes.labelsize": 18,
    "xtick.labelsize": 15,
    "ytick.labelsize": 15,
    "legend.fontsize": 14,
    "axes.labelweight": "bold",
    "figure.dpi": 110,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 1.1,
    "axes.grid": True,
    "grid.color": "#D9D9D9",
    "grid.linewidth": 0.8,
    "grid.alpha": 0.7,
})

# Paleta do projeto
COLORS = {
    "nanda": "#D62728",
    "noc":   "#1F77B4",
    "nic":   "#2CA02C",
    "orange": "#FF7F0E",
    "purple": "#9467BD",
    "brown":  "#8C564B",
    "gray":   "#7F7F7F",
}
PALETTE_SAFE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#56B4E9",
                "#CC79A7", "#9467BD", "#8C564B", "#1F77B4", "#FF7F0E"]

FONTE = "Fonte: camada derivada NANDA-I/NOC/NIC × MIMIC-IV Demo v2.2 (prova de conceito)"
AVISO = "Prova de conceito — não validado clinicamente"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def salvar(fig, nome):
    """Salva a figura APENAS em PNG (alta resolução)."""
    png = os.path.join(FIG_DIR, nome + ".png")
    fig.savefig(png, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  [OK] {nome}.png")


def rotulo_milhar(x, _pos=None):
    """Formata números no padrão brasileiro (20.566)."""
    return f"{int(round(x)):,}".replace(",", ".")


def fmt_br(x):
    """Formata número com separador decimal brasileiro."""
    return f"{x:.1f}".replace(".", ",")


def limpar_pdfs():
    """Remove PDFs antigos — o projeto passa a salvar somente PNG."""
    removidos = []
    for f in os.listdir(FIG_DIR):
        if f.lower().endswith(".pdf"):
            os.remove(os.path.join(FIG_DIR, f))
            removidos.append(f)
    if removidos:
        print(f"  [LIMPOU] {len(removidos)} PDF(s) antigo(s) removido(s).")


def contar_linhas(path):
    """Conta linhas (rápido, sem parsear) — inclui o cabeçalho."""
    n = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            n += chunk.count(b"\n")
    return n


# ---------------------------------------------------------------------------
# Carregamento dos dados
# ---------------------------------------------------------------------------
nanda = pd.read_csv(os.path.join(DATA_DIR, "fact_nanda_hypothesis.csv"))
evid = pd.read_csv(os.path.join(DATA_DIR, "mapping_nanda_evidence.csv"))
cand = pd.read_csv(os.path.join(DATA_DIR, "mapping_nanda_candidates.csv"))
noc = pd.read_csv(os.path.join(DATA_DIR, "fact_noc_measurement.csv"))
nic = pd.read_csv(os.path.join(DATA_DIR, "fact_nic_observed_proxy.csv"))
rec = pd.read_csv(os.path.join(DATA_DIR, "fact_nic_recommended.csv"))
nnn = pd.read_csv(os.path.join(DATA_DIR, "nnn_linkage_rules.csv"))
pac = pd.read_csv(os.path.join(DATA_DIR, "dim_patient.csv"))
adm = pd.read_csv(os.path.join(DATA_DIR, "admissions.csv"))
icu = pd.read_csv(os.path.join(DATA_DIR, "icustays.csv"))
svc = pd.read_csv(os.path.join(DATA_DIR, "services.csv"))

# ---------------------------------------------------------------------------
# Dicionários de tradução / acentuação
# ---------------------------------------------------------------------------
DOMINIOS = {
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

INDICADORES_NOC = {
    "GCS": "Escala de Coma de Glasgow (GCS)",
    "PA Sistolica": "Pressão Arterial Sistólica",
    "FC": "Frequência Cardíaca",
    "SpO2": "Saturação de Oxigênio (SpO₂)",
    "Temperatura": "Temperatura Corporal",
    "Dor NRS": "Intensidade da Dor (NRS)",
}

PROXIES_NIC = {
    "Adm. Medicamentos (proxy)": "Administração de Medicamentos (proxy)",
    "Terapia IV (proxy)": "Terapia Intravenosa (proxy)",
}

CAT_EVIDENCIA = {
    "Caracteristica definidora operacional": "Característica definidora operacional",
    "Condicao associada": "Condição associada",
}

METODO_INFERENCIA = {
    "clinical_threshold": "Limiar clínico operacional",
    "keyword_match": "Palavra-chave clínica",
    "transformer_embedding_fallback": "Fallback Transformer biomédico",
}

STATUS = {
    "rule_supported": "Suportada por regra",
    "candidate": "Candidata",
}

TIPO_ADMISSAO = {
    "EW EMER.": "Emergência (EW)",
    "OBSERVATION ADMIT": "Observação",
    "URGENT": "Urgente",
    "EU OBSERVATION": "Observação (EU)",
    "SURGICAL SAME DAY ADMISSION": "Cirurgia no mesmo dia",
    "DIRECT EMER.": "Emergência direta",
    "ELECTIVE": "Eletiva",
    "DIRECT OBSERVATION": "Observação direta",
    "AMBULATORY OBSERVATION": "Observação ambulatorial",
}

SEGURO = {"Other": "Outro", "Medicare": "Medicare", "Medicaid": "Medicaid"}

ESTADO_CIVIL = {
    "SINGLE": "Solteiro(a)",
    "MARRIED": "Casado(a)",
    "WIDOWED": "Viúvo(a)",
    "DIVORCED": "Divorciado(a)",
}

RACA = {
    "WHITE": "Branca",
    "BLACK/AFRICAN AMERICAN": "Negra/Afro-americana",
    "UNKNOWN": "Desconhecida",
    "HISPANIC/LATINO - CUBAN": "Hispânica/Latina — Cubana",
    "PORTUGUESE": "Portuguesa",
    "OTHER": "Outra",
    "UNABLE TO OBTAIN": "Não obtida",
    "BLACK/CAPE VERDEAN": "Negra/Cabo-verdiana",
    "WHITE - BRAZILIAN": "Branca — Brasileira",
    "HISPANIC/LATINO - SALVADORAN": "Hispânica/Latina — Salvadorenha",
    "PATIENT DECLINED TO ANSWER": "Recusou responder",
    "WHITE - OTHER EUROPEAN": "Branca — Europeia",
    "HISPANIC OR LATINO": "Hispânica/Latina",
    "HISPANIC/LATINO - PUERTO RICAN": "Hispânica/Latina — Porto-riquenha",
}

UNIDADE_UTI = {
    "Surgical Intensive Care Unit (SICU)": "UTI Cirúrgica (SICU)",
    "Medical Intensive Care Unit (MICU)": "UTI Clínica (MICU)",
    "Cardiac Vascular Intensive Care Unit (CVICU)": "UTI Cardiovascular (CVICU)",
    "Medical/Surgical Intensive Care Unit (MICU/SICU)": "UTI Clínico-Cirúrgica (MICU/SICU)",
    "Trauma SICU (TSICU)": "UTI Cirúrgica de Trauma (TSICU)",
    "Coronary Care Unit (CCU)": "Unidade Coronariana (CCU)",
    "Neuro Surgical Intensive Care Unit (Neuro SICU)": "UTI Neurocirúrgica (Neuro SICU)",
    "Neuro Stepdown": "Semi-intensiva Neurológica",
    "Neuro Intermediate": "Neurologia Intermediária",
}

SERVICO = {
    "MED": "Clínica Médica",
    "CMED": "Clínica Médica Cardíaca",
    "SURG": "Cirurgia",
    "OMED": "Clínica Médica (Outros)",
    "CSURG": "Cirurgia Cardíaca",
    "NSURG": "Neurocirurgia",
    "VSURG": "Cirurgia Vascular",
    "NMED": "Neurologia Médica",
    "TRAUM": "Trauma",
    "ORTHO": "Ortopedia",
    "PSYCH": "Psiquiatria",
    "TSURG": "Cirurgia Torácica",
    "GYN": "Ginecologia",
}

TABELAS_ENFERMAGEM = {
    "fact_nic_observed_proxy": "Proxies NIC observáveis",
    "mapping_nanda_evidence": "Evidências NANDA",
    "mapping_nanda_candidates": "Candidatos NANDA (top-k)",
    "fact_nanda_hypothesis": "Hipóteses NANDA-I",
    "fact_nic_recommended": "Recomendações NIC",
    "fact_noc_measurement": "Indicadores NOC",
    "nnn_linkage_rules": "Regras de ligação NNN",
}

DERIVADAS = {
    "dim_nanda_domain", "dim_patient", "dim_admission", "dim_icustay",
    "fact_nanda_hypothesis", "fact_noc_measurement",
    "fact_nic_observed_proxy", "fact_nic_recommended",
    "mapping_nanda_evidence", "mapping_nanda_candidates",
    "nnn_linkage_rules",
}


# ===========================================================================
# GRUPO 1 — RESULTADOS DA CAMADA DERIVADA NANDA-I / NOC / NIC
# ===========================================================================
print("Figura 1: Hipóteses NANDA-I por domínio...")
c1 = nanda["nanda_domain"].value_counts().sort_values()
c1.index = [DOMINIOS.get(d, d) for d in c1.index]
fig, ax = plt.subplots(figsize=(13, 8))
bars = ax.barh(c1.index, c1.values, color=COLORS["nanda"], height=0.62, alpha=0.9)
for b, v in zip(bars, c1.values):
    ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=17, fontweight="bold", color="#222222")
ax.set_xlabel("Número de Hipóteses NANDA-I Derivadas")
ax.set_title("Hipóteses Diagnósticas NANDA-I por Domínio", pad=18, loc="left")
ax.set_xlim(0, c1.max() * 1.16)
ax.xaxis.set_major_formatter(FuncFormatter(rotulo_milhar))
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.015, FONTE, fontsize=12, color="#777777")
salvar(fig, "Fig1_Hipoteses_NANDA")

print("Figura 2: Evidências por categoria...")
c2 = evid["evidence_category"].value_counts().sort_values()
c2.index = [CAT_EVIDENCIA.get(d, d) for d in c2.index]
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(c2.index, c2.values, color=[COLORS["noc"], COLORS["orange"]],
               height=0.55, alpha=0.9)
for b, v in zip(bars, c2.values):
    ax.text(b.get_width() + 250, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=18, fontweight="bold", color="#222222")
ax.set_xlabel("Número de Evidências")
ax.set_title("Evidências por Categoria", pad=18, loc="left")
ax.set_xlim(0, c2.max() * 1.18)
ax.xaxis.set_major_formatter(FuncFormatter(rotulo_milhar))
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, FONTE, fontsize=12, color="#777777")
salvar(fig, "Fig2_Evidencias")

print("Figura 2 (status): Status das hipóteses (barras)...")
c3 = nanda["status"].value_counts().sort_values()   # crescente -> maior no topo
labels3 = [STATUS.get(k, k) for k in c3.index]
valores3 = c3.values
pct3 = 100 * valores3 / valores3.sum()
cores3 = [COLORS["brown"], COLORS["nic"]]  # Candidata (embaixo), Suportada (topo)

fig, ax = plt.subplots(figsize=(12, 5.6))
bars = ax.barh(labels3, valores3, color=cores3, height=0.55, alpha=0.92)

# Valor + percentual grandes, centralizados DENTRO de cada barra (branco)
for b, v, p in zip(bars, valores3, pct3):
    ax.text(b.get_width() / 2, b.get_y() + b.get_height() / 2,
            f"{rotulo_milhar(v)}   ({fmt_br(p)}%)",
            va="center", ha="center", fontsize=22, fontweight="bold",
            color="white")
ax.set_xlabel("Número de Hipóteses")
ax.set_title(f"Status das Hipóteses NANDA-I  (n = {rotulo_milhar(int(valores3.sum()))})",
             pad=18, loc="left")
ax.set_xlim(0, max(valores3) * 1.18)
ax.xaxis.set_major_formatter(FuncFormatter(rotulo_milhar))
ax.grid(axis="y", visible=False)
ax.tick_params(axis="y", labelsize=19)
fig.text(0.01, -0.03,
         "Suportada por regra: correspondência por palavra-chave clínica.   "
         "Candidata: proposta por similaridade semântica (Transformer).",
         fontsize=12, color="#777777")
salvar(fig, "Fig2_Status_Hipoteses")

print("Figura 3: Evidências por método de inferência...")
c4 = evid["inference_method"].value_counts().sort_values()
c4.index = [METODO_INFERENCIA.get(d, d) for d in c4.index]
fig, ax = plt.subplots(figsize=(12, 6.5))
bars = ax.barh(c4.index, c4.values,
               color=[COLORS["noc"], COLORS["orange"], COLORS["purple"]],
               height=0.55, alpha=0.9)
for b, v in zip(bars, c4.values):
    ax.text(b.get_width() + 250, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=18, fontweight="bold", color="#222222")
ax.set_xlabel("Número de Evidências")
ax.set_title("Evidências por Método de Inferência", pad=18, loc="left")
ax.set_xlim(0, c4.max() * 1.18)
ax.xaxis.set_major_formatter(FuncFormatter(rotulo_milhar))
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, FONTE, fontsize=12, color="#777777")
salvar(fig, "Fig3_Evidencias_Categoria")

print("Figura 3 (pirâmide): Pirâmide etária...")
bins = [18, 30, 40, 50, 60, 70, 80, 130]
rotulos_etaria = ["18-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]
pac["faixa"] = pd.cut(pac["anchor_age"], bins=bins,
                      labels=rotulos_etaria, right=False)
tab = pd.crosstab(pac["faixa"], pac["gender"]).reindex(rotulos_etaria)
homens = tab.get("M", pd.Series(0, index=rotulos_etaria)).values
mulheres = tab.get("F", pd.Series(0, index=rotulos_etaria)).values

fig, ax = plt.subplots(figsize=(12, 7.5))
y = np.arange(len(rotulos_etaria))
ax.barh(y, -homens, color=COLORS["noc"], height=0.62, alpha=0.9, label="Masculino")
ax.barh(y, mulheres, color=COLORS["nanda"], height=0.62, alpha=0.85, label="Feminino")
for i, (h, m) in enumerate(zip(homens, mulheres)):
    if h:
        ax.text(-h - 0.3, i, str(h), va="center", ha="right",
                fontsize=16, fontweight="bold", color="#222222")
    if m:
        ax.text(m + 0.3, i, str(m), va="center", ha="left",
                fontsize=16, fontweight="bold", color="#222222")
ax.set_yticks(y)
ax.set_yticklabels(rotulos_etaria)
ax.set_xlabel("Número de Pacientes")
ax.set_title("Pirâmide Etária da Coorte", pad=18, loc="left")
lim = max(homens.max(), mulheres.max()) + 4
ax.set_xlim(-lim, lim)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(abs(x))}"))
ax.axvline(0, color="#444444", linewidth=1.1)
ax.grid(axis="y", visible=False)
ax.legend(loc="upper right", fontsize=15, frameon=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(pac)} pacientes",
         fontsize=12, color="#777777")
salvar(fig, "Fig3_Piramide")

print("Figura 4: Indicadores NOC...")
c5 = noc.groupby("indicator")["noc_measurement_id"].count().sort_values()
c5.index = [INDICADORES_NOC.get(d, d) for d in c5.index]
fig, ax = plt.subplots(figsize=(13, 7))
bars = ax.barh(c5.index, c5.values, color=COLORS["noc"], height=0.6, alpha=0.9)
for b, v in zip(bars, c5.values):
    ax.text(b.get_width() + 1.5, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=17, fontweight="bold", color="#222222")
ax.set_xlabel("Número de Medições Registradas")
ax.set_title("Indicadores NOC Vinculados às Hipóteses NANDA-I", pad=18, loc="left")
ax.set_xlim(0, c5.max() * 1.18)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         f"{FONTE}  •  indicadores operacionalizados, "
         "não documentados por enfermeiro.", fontsize=12, color="#777777")
salvar(fig, "Fig4_NOC")

print("Figura 5: Proxies NIC...")
c6 = nic["nic_label_proxy"].value_counts().sort_values()
c6.index = [PROXIES_NIC.get(d, d) for d in c6.index]
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(c6.index, c6.values,
               color=[COLORS["nic"], COLORS["orange"]], height=0.55, alpha=0.9)
for b, v in zip(bars, c6.values):
    ax.text(b.get_width() + 400, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=18, fontweight="bold", color="#222222")
ax.set_xlabel("Número de Eventos Registrados")
ax.set_title("Proxies NIC Observáveis", pad=18, loc="left")
ax.set_xlim(0, c6.max() * 1.16)
ax.xaxis.set_major_formatter(FuncFormatter(rotulo_milhar))
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         f"{FONTE}  •  registro não distingue prescritor "
         "nem confirma intervenção NIC autônoma.", fontsize=12, color="#777777")
salvar(fig, "Fig5_Proxies_NIC")


# ===========================================================================
# GRUPO 2 — DISTRIBUIÇÃO DO BANCO DE DADOS
# ===========================================================================
print("Figura 6: Distribuição de todas as tabelas do banco...")
arquivos = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
contagens = {f: max(0, contar_linhas(os.path.join(DATA_DIR, f)) - 1)
             for f in arquivos}
contagens = dict(sorted(contagens.items(), key=lambda kv: kv[1]))
nomes = [f[:-4] for f in contagens.keys()]
valores = list(contagens.values())
cores6 = [COLORS["nanda"] if (n[:-4] in DERIVADAS) else "#B0B0B0"
          for n in contagens.keys()]

fig, ax = plt.subplots(figsize=(13, 15))
bars = ax.barh(nomes, valores, color=cores6, height=0.68, alpha=0.9)
for b, v in zip(bars, valores):
    ax.text(b.get_width() * 1.04, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=12, fontweight="bold", color="#222222")
ax.set_xscale("log")
ax.set_xlabel("Número de Registros (escala logarítmica)")
ax.set_title("Distribuição do Banco de Dados — 42 Tabelas", pad=18, loc="left")
ax.set_xlim(1, max(valores) * 3)
ax.grid(axis="y", visible=False)
from matplotlib.patches import Patch
legend_handles = [
    Patch(color=COLORS["nanda"], label="Camada derivada de enfermagem"),
    Patch(color="#B0B0B0", label="Tabelas originais MIMIC-IV"),
]
ax.legend(handles=legend_handles, loc="lower right", frameon=False, fontsize=14)
fig.text(0.01, -0.01, f"{FONTE}  •  {sum(valores):,} registros no total".replace(",", "."),
         fontsize=12, color="#777777")
salvar(fig, "Fig6_Distribuicao_Tabelas")

print("Figura 7: Camada derivada de enfermagem...")
c7 = pd.Series({
    "Proxies NIC observáveis": len(nic),
    "Evidências NANDA": len(evid),
    "Candidatos NANDA (top-k)": len(cand),
    "Hipóteses NANDA-I": len(nanda),
    "Recomendações NIC": len(rec),
    "Indicadores NOC": len(noc),
    "Regras de ligação NNN": len(nnn),
}).sort_values()
fig, ax = plt.subplots(figsize=(12, 6.5))
bars = ax.barh(c7.index, c7.values, color=COLORS["nic"], height=0.6, alpha=0.9)
for b, v in zip(bars, c7.values):
    ax.text(b.get_width() + 60, b.get_y() + b.get_height() / 2,
            rotulo_milhar(v), va="center", ha="left",
            fontsize=17, fontweight="bold", color="#222222")
ax.set_xlabel("Número de Registros")
ax.set_title("Camada Derivada de Enfermagem (NANDA-I / NOC / NIC)",
             pad=18, loc="left")
ax.set_xlim(0, c7.max() * 1.15)
ax.xaxis.set_major_formatter(FuncFormatter(rotulo_milhar))
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, FONTE, fontsize=12, color="#777777")
salvar(fig, "Fig7_Camada_Enfermagem")


# ===========================================================================
# GRUPO 3 — PERFIL DOS PACIENTES
# ===========================================================================
print("Figura 8: Distribuição etária por sexo...")
fig, ax = plt.subplots(figsize=(12, 6.5))
for gen, cor, lab in [("M", COLORS["noc"], "Masculino"),
                      ("F", COLORS["nanda"], "Feminino")]:
    ax.hist(pac.loc[pac["gender"] == gen, "anchor_age"],
            bins=np.arange(20, 101, 10), alpha=0.65, color=cor, label=lab)
ax.set_xlabel("Idade (anos)")
ax.set_ylabel("Número de Pacientes")
ax.set_title("Distribuição Etária dos Pacientes por Sexo", pad=18, loc="left")
ax.legend(frameon=False, fontsize=15)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(pac)} pacientes", fontsize=12, color="#777777")
salvar(fig, "Fig8_Perfil_Idade")

print("Figura 9: Tipo de admissão...")
c9 = adm["admission_type"].value_counts().sort_values()
c9.index = [TIPO_ADMISSAO.get(d, d) for d in c9.index]
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(c9.index, c9.values, color=COLORS["noc"], height=0.62, alpha=0.9)
for b, v in zip(bars, c9.values):
    ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Admissões")
ax.set_title("Perfil dos Pacientes — Tipo de Admissão Hospitalar", pad=18, loc="left")
ax.set_xlim(0, c9.max() * 1.15)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(adm)} admissões", fontsize=12, color="#777777")
salvar(fig, "Fig9_Perfil_Tipo_Admissao")

print("Figura 10: Seguro de saúde...")
c10 = adm["insurance"].value_counts().sort_values()
c10.index = [SEGURO.get(d, d) for d in c10.index]
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(c10.index, c10.values, color=[COLORS["noc"], COLORS["orange"], COLORS["nic"]],
              width=0.55, alpha=0.9)
for b, v in zip(bars, c10.values):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, str(v),
            ha="center", va="bottom", fontsize=18, fontweight="bold",
            color="#222222")
ax.set_ylabel("Número de Admissões")
ax.set_title("Perfil dos Pacientes — Seguro de Saúde", pad=18, loc="left")
ax.set_ylim(0, c10.max() * 1.15)
ax.grid(axis="x", visible=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(adm)} admissões", fontsize=12, color="#777777")
salvar(fig, "Fig10_Perfil_Seguro")

print("Figura 11: Estado civil...")
c11 = adm["marital_status"].fillna("Não informado").value_counts().sort_values()
c11.index = [ESTADO_CIVIL.get(d, d) for d in c11.index]
fig, ax = plt.subplots(figsize=(11, 6.5))
bars = ax.barh(c11.index, c11.values, color=COLORS["purple"], height=0.6, alpha=0.9)
for b, v in zip(bars, c11.values):
    ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Admissões")
ax.set_title("Perfil dos Pacientes — Estado Civil", pad=18, loc="left")
ax.set_xlim(0, c11.max() * 1.15)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(adm)} admissões", fontsize=12, color="#777777")
salvar(fig, "Fig11_Perfil_Estado_Civil")

print("Figura 12: Raça/etnia...")
c12 = adm["race"].map(lambda r: RACA.get(r, "Outras")).value_counts().sort_values()
fig, ax = plt.subplots(figsize=(12, 7.5))
bars = ax.barh(c12.index, c12.values, color=COLORS["orange"], height=0.62, alpha=0.9)
for b, v in zip(bars, c12.values):
    ax.text(b.get_width() + 1.5, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=15, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Admissões")
ax.set_title("Perfil dos Pacientes — Raça/Etnia", pad=18, loc="left")
ax.set_xlim(0, c12.max() * 1.12)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(adm)} admissões", fontsize=12, color="#777777")
salvar(fig, "Fig12_Perfil_Raca_Etnia")

print("Figura 13: Unidades de UTI...")
c13 = icu["first_careunit"].value_counts().sort_values()
c13.index = [UNIDADE_UTI.get(d, d) for d in c13.index]
fig, ax = plt.subplots(figsize=(12.5, 7.5))
bars = ax.barh(c13.index, c13.values, color=COLORS["nic"], height=0.6, alpha=0.9)
for b, v in zip(bars, c13.values):
    ax.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=15, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Estadias em UTI")
ax.set_title("Perfil dos Pacientes — Unidade de UTI de Entrada", pad=18, loc="left")
ax.set_xlim(0, c13.max() * 1.15)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(icu)} estadias em UTI", fontsize=12, color="#777777")
salvar(fig, "Fig13_Perfil_Unidades_UTI")

print("Figura 14: Tempo de permanência em UTI...")
fig, ax = plt.subplots(figsize=(12, 6.5))
ax.hist(icu["los"], bins=np.arange(0, 21, 1), color=COLORS["noc"],
        alpha=0.85, edgecolor="white", linewidth=1.2)
ax.axvline(icu["los"].median(), color=COLORS["nanda"], linewidth=2.5,
           linestyle="--")
ax.text(icu["los"].median() + 0.4, ax.get_ylim()[1] * 0.85,
        f"Mediana = {fmt_br(icu['los'].median())} dias",
        color=COLORS["nanda"], fontsize=15, fontweight="bold")
ax.set_xlabel("Tempo de Permanência na UTI (dias)")
ax.set_ylabel("Número de Estadias")
ax.set_title("Perfil dos Pacientes — Tempo de Permanência em UTI",
             pad=18, loc="left")
fig.text(0.01, -0.02, f"{FONTE}  •  {len(icu)} estadias em UTI", fontsize=12, color="#777777")
salvar(fig, "Fig14_Perfil_LOS_UTI")

print("Figura 15: Serviços clínicos...")
c15 = svc["curr_service"].value_counts().sort_values()
c15.index = [SERVICO.get(d, d) for d in c15.index]
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(c15.index, c15.values, color=COLORS["noc"], height=0.62, alpha=0.9)
for b, v in zip(bars, c15.values):
    ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Transferências de Serviço")
ax.set_title("Perfil dos Pacientes — Serviços Clínicos", pad=18, loc="left")
ax.set_xlim(0, c15.max() * 1.15)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02, f"{FONTE}  •  {len(svc)} registros de serviço", fontsize=12, color="#777777")
salvar(fig, "Fig15_Perfil_Servicos")

print("Figura 16: Desfecho hospitalar...")
obitos = int(adm["hospital_expire_flag"].sum())
sobrev = int(len(adm) - obitos)
fig, ax = plt.subplots(figsize=(10, 6.5))
barras16 = ax.bar(["Sobreviventes", "Óbitos"], [sobrev, obitos],
                  color=[COLORS["nic"], COLORS["nanda"]], width=0.5, alpha=0.9)
for b, v in zip(barras16, [sobrev, obitos]):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
            f"{v}  ({fmt_br(100 * v / len(adm))}%)",
            ha="center", va="bottom", fontsize=19, fontweight="bold",
            color="#222222")
ax.set_ylabel("Número de Admissões")
ax.set_title("Perfil dos Pacientes — Desfecho Hospitalar", pad=18, loc="left")
ax.set_ylim(0, max(sobrev, obitos) * 1.18)
ax.grid(axis="x", visible=False)
fig.text(0.01, -0.02,
         f"{FONTE}  •  mortalidade hospitalar de {fmt_br(100 * obitos / len(adm))}%",
         fontsize=12, color="#777777")
salvar(fig, "Fig16_Perfil_Desfecho")


# ===========================================================================
# GRUPO 4 — ASPECTOS DO MÉTODO DE INFERÊNCIA
# ===========================================================================
print("Figura 17: Escore de similaridade semântica...")
fig, ax = plt.subplots(figsize=(12, 6.5))
ax.hist(cand["similarity_score"], bins=40, color=COLORS["purple"],
        alpha=0.85, edgecolor="white", linewidth=1.2)
ax.axvline(cand["similarity_score"].median(), color=COLORS["nanda"],
           linewidth=2.5, linestyle="--")
ax.text(cand["similarity_score"].median() + 0.005, ax.get_ylim()[1] * 0.85,
        f"Mediana = {cand['similarity_score'].median():.3f}",
        color=COLORS["nanda"], fontsize=15, fontweight="bold")
ax.set_xlabel("Escore de Similaridade Semântica (cosseno)")
ax.set_ylabel("Número de Candidatos")
ax.set_title("Método — Similaridade Semântica dos Candidatos NANDA-I",
             pad=18, loc="left")
fig.text(0.01, -0.02,
         "Modelo: pritamdeka/S-BioBERT-snli-multinli-stsb (Transformer biomédico).",
         fontsize=12, color="#777777")
salvar(fig, "Fig17_Metodo_Similaridade")

print("Figura 18: Similaridade por posição no ranking...")
fig, ax = plt.subplots(figsize=(11, 6.5))
dados_rank = [cand.loc[cand["rank_position"] == r, "similarity_score"]
              for r in [1, 2, 3]]
bp = ax.boxplot(dados_rank, tick_labels=["1º lugar", "2º lugar", "3º lugar"],
                patch_artist=True, widths=0.5,
                medianprops=dict(color="#222222", linewidth=2))
for patch, cor in zip(bp["boxes"], [COLORS["noc"], COLORS["orange"], COLORS["gray"]]):
    patch.set_facecolor(cor)
    patch.set_alpha(0.75)
ax.set_ylabel("Escore de Similaridade Semântica")
ax.set_xlabel("Posição do Domínio Candidato no Ranking")
ax.set_title("Método — Similaridade Decresce com a Posição do Ranking",
             pad=18, loc="left")
ax.grid(axis="x", visible=False)
fig.text(0.01, -0.02,
         f"{len(cand)} candidatos (666 códigos ICD × 3 posições).",
         fontsize=12, color="#777777")
salvar(fig, "Fig18_Metodo_Rank_Similaridade")

print("Figura 19: Evidências por hipótese...")
c19 = nanda["n_evidence"].astype(float)
fig, ax = plt.subplots(figsize=(12, 6.5))
ax.hist(c19, bins=np.logspace(0, np.log10(c19.max() + 1), 30),
        color=COLORS["noc"], alpha=0.85, edgecolor="white", linewidth=1.2)
ax.set_xscale("log")
ax.set_xlabel("Número de Evidências por Hipótese (escala logarítmica)")
ax.set_ylabel("Número de Hipóteses")
ax.set_title("Método — Quantidade de Evidências por Hipótese NANDA-I",
             pad=18, loc="left")
fig.text(0.01, -0.02,
         f"Mediana = {c19.median():.0f} evidências • máximo = {c19.max():.0f}.",
         fontsize=12, color="#777777")
salvar(fig, "Fig19_Metodo_Evidencias_Hipotese")

print("Figura 20: Correspondência por palavra-chave...")
kw = int(nanda["has_keyword_match"].sum())
sem = int(len(nanda) - kw)
fig, ax = plt.subplots(figsize=(10, 6.5))
barras20 = ax.bar(["Com palavra-chave", "Apenas semântico"], [kw, sem],
                  color=[COLORS["nic"], COLORS["purple"]], width=0.5, alpha=0.9)
for b, v in zip(barras20, [kw, sem]):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 10,
            f"{v}  ({fmt_br(100 * v / len(nanda))}%)",
            ha="center", va="bottom", fontsize=19, fontweight="bold",
            color="#222222")
ax.set_ylabel("Número de Hipóteses")
ax.set_title("Método — Hipóteses com Correspondência por Palavra-chave",
             pad=18, loc="left")
ax.set_ylim(0, max(kw, sem) * 1.18)
ax.grid(axis="x", visible=False)
fig.text(0.01, -0.02,
         "Palavra-chave: regra transparente e auditável. Semântico: fallback por Transformer.",
         fontsize=12, color="#777777")
salvar(fig, "Fig20_Metodo_Keyword_Transformer")

print("Figura 21: Regras de ligação NNN...")
c21 = nnn["nanda_domain"].value_counts().sort_values()
c21.index = [DOMINIOS.get(d, d) for d in c21.index]
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(c21.index, c21.values, color=COLORS["orange"], height=0.6, alpha=0.9)
for b, v in zip(bars, c21.values):
    ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Regras de Ligação")
ax.set_title("Método — Regras de Ligação NANDA-NOC-NIC por Domínio",
             pad=18, loc="left")
ax.set_xlim(0, c21.max() * 1.3)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         f"{len(nnn)} regras documentadas (Moorhead et al., 2024).",
         fontsize=12, color="#777777")
salvar(fig, "Fig21_Metodo_NNN_Ligacoes")

print("Figura 22: Recomendações NIC mais frequentes...")
c22 = rec["nic_label"].value_counts().sort_values()
fig, ax = plt.subplots(figsize=(12, 6.5))
bars = ax.barh(c22.index, c22.values, color=COLORS["nic"], height=0.6, alpha=0.9)
for b, v in zip(bars, c22.values):
    ax.text(b.get_width() + 2, b.get_y() + b.get_height() / 2,
            str(v), va="center", ha="left", fontsize=16, fontweight="bold",
            color="#222222")
ax.set_xlabel("Número de Recomendações")
ax.set_title("Método — Recomendações NIC Derivadas por Regras NNN",
             pad=18, loc="left")
ax.set_xlim(0, c22.max() * 1.15)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.02,
         f"{len(rec)} recomendações • confiança: BAIXO • fonte: Moorhead et al., 2024.",
         fontsize=12, color="#777777")
salvar(fig, "Fig22_Metodo_Recomendacoes_NIC")


# ---------------------------------------------------------------------------
# Limpeza final e resumo
# ---------------------------------------------------------------------------
limpar_pdfs()
print(f"\nTodas as figuras foram salvas em: {FIG_DIR}")
print("Formato: somente PNG (200 dpi), fontes ampliadas para slides.")
