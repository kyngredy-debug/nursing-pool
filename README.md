# nursing-pool

## Prova de conceito computacional para uma camada derivada NANDA-I/NOC/NIC no MIMIC-IV Demo

**Autores:** Kerolyne Yngredy Rodrigues Santos, Ryan de Paulo Santos, Karla Rangel Ribeiro

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Proof of Concept](https://img.shields.io/badge/Status-Proof%20of%20Concept-orange.svg)]()

> **Aviso metodológico essencial:** este projeto não identifica diagnósticos de enfermagem reais no MIMIC-IV. O MIMIC-IV Demo v2.2 não contém registros nativos NANDA-I, NOC ou NIC documentados por enfermeiros. O repositório constrói uma camada derivada, exploratória, auditável e reprodutível para prova de conceito computacional.

---

## Estrutura do repositório

```text
nursing-pool/
├── rebuild_transformer_embeddings.py   # Pipeline principal (Python)
├── rebuild_keywords.py                 # Wrapper de compatibilidade (deprecated)
├── add_clinical_tables.py              # Adiciona tabelas clínicas MIMIC ao banco
├── config.py                           # Configuração do pipeline principal
├── requirements.txt                    # Dependências Python (pipeline principal)
│
├── R/                                  # Pipeline legado em R (modo sintético)
│   ├── pipeline.R                      # Orquestrador do pipeline R
│   ├── 01_data_access.R … 15_compliance_report.R
│   ├── config.R                        # Configuração do pipeline R
│   ├── theme_cellpress.R               # Tema gráfico Cell Press
│   ├── synthetic_data.R                # Geração de dados sintéticos
│   └── requirements.R                  # Dependências R
│
├── scripts/                            # Geradores de figuras e análises
│   ├── gerar_figuras_slides.py         # Figuras em PT-BR com fontes ampliadas
│   ├── gerar_sankey.py                 # Diagrama de Sankey metodológico
│   └── analises_demonstracao.py        # Análises demonstrativas NNN
│
├── data/                               # CSVs publicados (42 tabelas)
├── docs/                               # Documentação metodológica e site estático
├── output/                             # Figuras e relatórios gerados
├── tests/                              # Testes automatizados (pytest)
├── Dockerfile                          # Container do pipeline R
├── renv.lock                           # Ambiente R (renv)
├── CITATION.cff                        # Metadados de citação
└── LICENSE
```

## Tese metodológica

O objetivo do projeto é demonstrar a viabilidade de uma arquitetura relacional orientada à enfermagem a partir de dados clínicos existentes. A contribuição não é afirmar acurácia diagnóstica, validar intervenções ou mensurar resultados assistenciais. A contribuição é separar e documentar três níveis:

1. **Dado clínico observado:** SpO2, frequência cardíaca, pressão arterial, temperatura, GCS, dor, exames, medicamentos, fluidos, admissões e códigos ICD.
2. **Evidência operacional:** hipoxemia, taquicardia, hipotensão, febre, dor intensa, alteração neurológica e correspondências por palavras-chave clínicas.
3. **Inferência terminológica exploratória:** hipóteses computacionais NANDA-I, indicadores NOC operacionalizados, proxies observáveis de intervenções NIC e recomendações NIC derivadas por regras de ligação NANDA-NOC-NIC.

## Método atual

O pipeline principal é `rebuild_transformer_embeddings.py`.

O mapeamento NANDA-I usa:

1. regras por palavras-chave clínicas para correspondências transparentes e auditáveis;
2. fallback semântico por embeddings de Transformer biomédico para descrições ICD sem correspondência direta.

Modelo padrão:

```text
pritamdeka/S-BioBERT-snli-multinli-stsb
```

O Transformer é usado para ranqueamento semântico por similaridade de cosseno. Ele não é classificador clínico, não substitui julgamento profissional e não valida diagnósticos. O antigo fallback por TF-IDF foi substituído no pipeline principal e aparece apenas como histórico metodológico.

O pipeline em R (pasta `R/`) é mantido para compatibilidade com o modo sintético; o pipeline em Python é o método principal para dados reais.

## Números congelados da versão atual

| Item | Contagem |
|:---|---:|
| Pacientes | 100 |
| Admissões hospitalares | 275 |
| Estadias em UTI | 140 |
| Tabelas SQLite | 42 |
| Registros em `chartevents` | 668.862 |
| Exames em `labevents` | 107.727 |
| Eventos em `emar` | 35.835 |
| Evidências em `mapping_nanda_evidence` | 25.072 |
| Candidatos top-k em `mapping_nanda_candidates` | 1.998 |
| Hipóteses computacionais NANDA-I | 1.629 |
| Indicadores NOC operacionalizados | 685 |
| Proxies observáveis de intervenções NIC | 55.233 |
| Recomendações NIC derivadas por regras NNN | 1.365 |

Distribuição das evidências:

| Método | Registros |
|:---|---:|
| Limiar clínico operacional | 20.566 |
| Palavra-chave clínica | 2.644 |
| Fallback Transformer | 1.862 |

## Tabelas principais

| Tabela | Interpretação segura |
|:---|:---|
| `mapping_nanda_evidence` | Evidências operacionais ou semânticas com método, escore, modelo e limitação |
| `mapping_nanda_candidates` | Ranking top-k de domínios NANDA-I candidatos para ICDs sem keyword match |
| `fact_nanda_hypothesis` | Hipóteses computacionais NANDA-I, não diagnósticos confirmados |
| `fact_noc_measurement` | Indicadores NOC operacionalizados por variáveis observáveis |
| `fact_nic_observed_proxy` | Proxies observáveis associados a ações assistenciais interdisciplinares |
| `fact_nic_recommended` | Recomendações NIC derivadas por regras NANDA-NOC-NIC |
| `nnn_linkage_rules` | Regras documentadas de ligação terminológica |

## Figuras e análises disponíveis

O repositório inclui figuras prontas (PNG, em português, com fontes ampliadas para
apresentações) em `output/figures/`:

- **Exploração dos dados** — distribuição do banco (42 tabelas), perfil dos
  pacientes (idade, sexo, tipo de admissão, seguro, raça, UTI, serviços, desfecho)
  e aspectos do método (similaridade semântica, keyword vs. Transformer, regras NNN).
- **Fluxo metodológico** — `Sankey_Metodologia.png`, diagrama do pipeline
  NANDA-I/NOC/NIC.
- **Análises demonstrativas** — `FigA_*` a `FigG_*` mostrando o valor de uma base
  NNN integrada: rastreamento de desfechos (admissão vs. follow-up), vínculo
  diagnóstico→resultado→intervenção e associação entre carga diagnóstica e
  desfechos (tempo de UTI, mortalidade). Ver `output/ANALISES_DEMONSTRACAO.md`.

Para regenerar:

```bash
python scripts/gerar_figuras_slides.py
python scripts/gerar_sankey.py
python scripts/analises_demonstracao.py
```

## Interpretação segura dos resultados

- Uma hipótese computacional NANDA-I é uma sugestão derivada de evidências parciais. Não é diagnóstico de enfermagem confirmado.
- Um indicador NOC operacionalizado é uma aproximação baseada em variável clínica observável. Não é resultado NOC documentado por enfermeiro.
- Um proxy observável de intervenção NIC é um evento registrado, como medicamento ou fluido IV. Não prova intervenção NIC autônoma realizada por enfermeiro.
- Uma recomendação NIC derivada por regras NNN é uma ligação teórica. Não é prescrição clínica nem conduta assistencial individual.

## O que este projeto não faz

- Não extrai diagnósticos NANDA-I reais do MIMIC-IV.
- Não valida clinicamente hipóteses NANDA-I.
- Não mensura resultados NOC documentados no prontuário por enfermeiros.
- Não comprova execução autônoma de intervenção NIC por enfermeiros.
- Não estima acurácia diagnóstica, AUC, desempenho preditivo ou utilidade assistencial.
- Não substitui avaliação de especialista, julgamento clínico ou validação terminológica.

## Como reproduzir

```bash
git clone https://github.com/kyngredy-debug/nursing-pool.git
cd nursing-pool
pip install -r requirements.txt

# Baixe o MIMIC-IV Demo v2.2 e extraia ao lado do repositório:
# ../mimic-iv-clinical-database-demo-2.2/

python rebuild_transformer_embeddings.py
pytest
```

O pipeline gera `output/nursing_db.sqlite` e exporta CSVs para `data/`, usados pelo site estático.

Pipeline R (legado, modo sintético):

```bash
Rscript R/pipeline.R --mode=synthetic
```

## Consultas SQL prudentes

```sql
SELECT inference_method, COUNT(*) AS n
FROM mapping_nanda_evidence
GROUP BY inference_method
ORDER BY n DESC;
```

```sql
SELECT nanda_domain, COUNT(*) AS n
FROM fact_nanda_hypothesis
GROUP BY nanda_domain
ORDER BY n DESC;
```

```sql
SELECT icd_code, candidate_domain, similarity_score, rank_position, model_name
FROM mapping_nanda_candidates
WHERE accepted_as_top1 = 1
LIMIT 20;
```

## Limitações

- O MIMIC-IV Demo é pequeno e não representa validação clínica.
- NANDA-I, NOC e NIC não são registros nativos do MIMIC-IV.
- Não houve validação por enfermeiros especialistas.
- Regras heurísticas e descrições resumidas podem introduzir viés terminológico.
- Embeddings de Transformer ranqueiam similaridade textual ou conceitual, não julgamento clínico.
- Proxies NIC não distinguem prescritor, executor, autonomia profissional ou intenção terapêutica.
- O uso das taxonomias NANDA-I, NOC e NIC é limitado a identificadores e descrições resumidas, respeitando direitos autorais.
- A camada derivada não deve ser usada para decisão assistencial.

## Site

Consulta SQL estática: https://kyngredy-debug.github.io/nursing-pool/

O site carrega os CSVs publicados em `data/` e inclui aviso visível sobre a natureza exploratória, derivada e não validada clinicamente da camada NANDA-I/NOC/NIC.

## Licença

MIT License. Veja `LICENSE`.
