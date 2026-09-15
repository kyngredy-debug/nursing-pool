# Análises Demonstrativas — Banco NANDA-I / NOC / NIC

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
  **ρ = 0.39** (p = 0.000).
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
