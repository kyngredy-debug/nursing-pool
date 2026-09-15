#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nic_completo.py
===============
Mostra o panorama COMPLETO das intervenções NIC que podem ser derivadas
da base MIMIC-IV Demo v2.2 — muito além dos 2 proxies atualmente
materializados em fact_nic_observed_proxy (medicamentos e terapia IV).

A camada derivada atual captura apenas:
    - Administração de Medicamentos (NIC 2300) — via eMAR
    - Terapia Intravenosa (NIC 4200) — via inputevents

Porém os dados brutos do MIMIC suportam ~12 intervenções NIC, totalizando
cerca de 480 mil registros. Esta figura evidencia esse potencial.

Saída: output/figures/Fig_NIC_Completo.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "output", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 16,
    "axes.titlesize": 21,
    "axes.titleweight": "bold",
    "axes.labelsize": 17,
    "xtick.labelsize": 14,
    "ytick.labelsize": 15,
    "axes.labelweight": "bold",
    "figure.dpi": 110,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 1.1,
    "axes.grid": True,
    "grid.color": "#D9D9D9",
    "grid.linewidth": 0.8,
    "grid.alpha": 0.7,
})

COR_NIC = "#2CA02C"          # verde — NIC
COR_ATUAL = "#B0B0B0"        # cinza — proxies atuais


def br(n):
    return f"{int(round(n)):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Carregamento e cômputo
# ---------------------------------------------------------------------------
ditems = pd.read_csv(os.path.join(DATA_DIR, "d_items.csv"))
dmap = ditems.set_index("itemid")[["category"]].to_dict("index")

ce = pd.read_csv(os.path.join(DATA_DIR, "chartevents.csv"), usecols=["itemid"])
ce["cat"] = ce["itemid"].map(lambda i: dmap.get(i, {}).get("category", "?"))

ie = pd.read_csv(os.path.join(DATA_DIR, "inputevents.csv"))
oe = pd.read_csv(os.path.join(DATA_DIR, "outputevents.csv"))
emar = pd.read_csv(os.path.join(DATA_DIR, "emar.csv"))

iv = ie["ordercategoryname"].isin([
    "01-Drips", "02-Fluids (Crystalloids)", "03-IV Fluid Bolus",
    "04-Fluids (Colloids)", "05-Med Bolus", "07-Blood Products",
    "08-Antibiotics (IV)", "10-Prophylaxis (IV)",
]).sum()

skin = int(((ce["cat"] == "Skin - Assessment")
            | (ce["cat"] == "Skin - Impairment")
            | (ce["cat"] == "Skin - Incisions")).sum())

# NIC -> contagem de registros deriváveis (ordem decrescente)
nic_data = pd.Series({
    "Monitorização de Sinais Vitais (6680)": int((ce["cat"] == "Routine Vital Signs").sum()),
    "Posicionamento / Contenção (0840)": int((ce["cat"] == "Restraint/Support Systems").sum()),
    "Oxigenoterapia (3320)": int((ce["cat"] == "Respiratory").sum()),
    "Monitorização Neurológica (2620)": int((ce["cat"] == "Neurological").sum()),
    "Prevenção de Úlcera por Pressão (3540)": skin,
    "Controle da Dor (1400)": int((ce["cat"] == "Pain/Sedation").sum()),
    "Administração de Medicamentos (2300)": len(emar),
    "Controle de Eliminação (0590)": int((ce["cat"] == "GI/GU").sum()),
    "Terapia Intravenosa (4200)": int(iv),
    "Controle Hídrico (4120)": len(oe),
    "Nutrição Enteral (1056)": int((ie["ordercategoryname"] == "13-Enteral Nutrition").sum()),
    "Nutrição Parenteral (1200)": int((ie["ordercategoryname"] == "12-Parenteral Nutrition").sum()),
}).sort_values()

# Destaque: os 2 proxies atualmente materializados na camada derivada
atualmente = {"Administração de Medicamentos (2300)", "Terapia Intravenosa (4200)"}

fig, ax = plt.subplots(figsize=(13, 9))
cores = [COR_ATUAL if k in atualmente else COR_NIC for k in nic_data.index]
bars = ax.barh(nic_data.index, nic_data.values, color=cores, height=0.65, alpha=0.92)

for b, v in zip(bars, nic_data.values):
    ax.text(b.get_width() * 1.04, b.get_y() + b.get_height() / 2,
            br(v), va="center", ha="left",
            fontsize=15, fontweight="bold", color="#222222")

ax.set_xscale("log")
ax.set_xlabel("Número de Registros (escala logarítmica)")
ax.set_title("Intervenções NIC Deriváveis da Base MIMIC-IV",
             pad=18, loc="left")
ax.set_xlim(1, nic_data.max() * 3)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: br(x)))
ax.grid(axis="y", visible=False)

from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(color=COR_ATUAL, label="Proxies atuais (2)"),
    Patch(color=COR_NIC, label="Intervenções adicionais deriváveis (10)"),
], loc="lower right", frameon=False, fontsize=14)

fig.text(0.01, -0.015,
         "A camada derivada atual materializa apenas 2 proxies NIC (medicamentos e terapia IV). "
         "Os dados brutos do MIMIC-IV Demo suportam ~12 intervenções NIC (~480 mil registros).",
         fontsize=12, color="#777777")

png = os.path.join(FIG_DIR, "Fig_NIC_Completo.png")
fig.savefig(png, bbox_inches="tight", dpi=200)
plt.close(fig)
print(f"[OK] {png}")
print(f"Total de registros NIC deriváveis: {int(nic_data.sum()):,}".replace(",", "."))
