# FOSP_Cancer
## Casos de Câncer no Estado de São Paulo (FOSP) - Dashboard Interativo
Este projeto é um dashboard interativo desenvolvido em Python com Streamlit para análise exploratória, visualização e estudo de sobrevivência de casos de câncer no estado de São Paulo, utilizando dados da Fundação Oncocentro de São Paulo (FOSP).

### Funcionalidades Principais
Visualização Interativa:

Filtros dinâmicos por DRS, município, tipo de câncer, hospital e período.

Métricas rápidas de casos totais, por sexo e tempo médio diagnóstico-tratamento.

Mapa coroplético dos casos por município (Folium).

Gráficos de barras, linhas, pizza e tornado para diferentes aspectos dos dados (Plotly).

### Gestão de Dados:

Análise de registros por mês e hospital.

Frequência de especialidades.

Tabelas de percentuais e cruzamentos por faixa de ano e tipo de diagnóstico.

### Curvas de Sobrevivência:

Análise de sobrevida Kaplan-Meier para diferentes tipos de câncer.

Filtros customizados para seleção de subgrupos.

Mock-ups de possíveis visualizações e modelos de pesquisa.

# Pré-requisitos
Python 3.8+

Instale as dependências com:

bash
pip install -r requirements.txt
Principais bibliotecas utilizadas:

streamlit

pandas

numpy

folium

plotly

matplotlib

seaborn

lifelines

requests

beautifulsoup4

pyarrow

pillow

streamlit-folium


## Estrutura das Páginas
### Visão Geral:
Métricas principais, mapa interativo, gráficos de casos por sexo, tipo de câncer, faixa etária, motivos de não tratamento, tipos de tratamento e situação final dos pacientes.

### Gestão de Dados:
Análise temporal dos registros, frequência de especialidades, tabelas de percentuais de diagnósticos.

### Curva de Sobrevivência:
Seleção e análise de subgrupos de câncer, geração de curvas Kaplan-Meier e visualização de mock-ups de modelos de pesquisa.

## Personalização e Estilo
Customização visual via CSS externo (style.css).

Logotipos institucionais e identidade visual do Governo do Estado de SP e FOSP.
