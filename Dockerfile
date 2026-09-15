# =============================================================================
# Dockerfile - Containerização do Pipeline de Enfermagem MIMIC-IV
# =============================================================================
# Garante portabilidade total do pipeline em qualquer máquina com Docker.
#
# Build:
#   docker build -t mimic-nursing-poc .
#
# Run (modo sintético):
#   docker run --rm -v $(pwd)/output:/app/output mimic-nursing-poc
#
# Run (modo real, montando diretório de dados):
#   docker run --rm -v /path/to/mimic-iv:/data -v $(pwd)/output:/app/output \
#     mimic-nursing-poc --mode=real --data_dir=/data
#
# Shell interativo:
#   docker run -it --rm mimic-nursing-poc R
# =============================================================================

FROM rocker/r-ver:4.3.2

LABEL maintainer="Enfermagem de Precisão POC"
LABEL description="Pipeline MIMIC-IV → NANDA/NOC/NIC para Enfermagem de Precisão"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    zlib1g-dev \
    libgsl-dev \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar scripts do pipeline
COPY R/config.R R/
COPY R/theme_cellpress.R R/
COPY R/synthetic_data.R R/
COPY R/requirements.R R/
COPY R/01_data_access.R R/
COPY R/02_nursing_mapping.R R/
COPY R/03_nanda_diagnostics.R R/
COPY R/04_noc_outcomes.R R/
COPY R/05_nic_interventions.R R/
COPY R/06_nursing_db.R R/
COPY R/07_statistical_analysis.R R/
COPY R/08_visualization.R R/
COPY R/09_audit.R R/
COPY R/10_benchmark.R R/
COPY R/pipeline.R R/

# Criar diretórios de saída
RUN mkdir -p output/cache output/figures

# Instalar pacotes R
RUN Rscript R/requirements.R

# Ponto de entrada
ENTRYPOINT ["Rscript", "R/pipeline.R"]

# Argumentos padrão: modo sintético
CMD ["--mode=synthetic"]
