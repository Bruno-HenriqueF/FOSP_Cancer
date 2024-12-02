#%%
import folium.features
import folium.map
import pandas as pd
import plotly.express as px
import json
import numpy as np
from urllib.request import urlopen
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
import pdfkit
import requests

# URL para baixar o arquivo CSV
file_id = '1-rPhBKe1rHkov8K1xhK8iE9fcscl4y4d'
url = f"https://drive.google.com/uc?id={file_id}"

# Fazer o download do arquivo
r = requests.get(url)

# Salvar o conteúdo como um arquivo CSV com o nome 'pacientes_geral'
pacientes_geral = 'pacientes_geral.csv'  # Nome da variável com o caminho do arquivo

# Salvar o arquivo localmente
with open(pacientes_geral, 'wb') as f:
    f.write(r.content)

# Agora, podemos carregar o arquivo CSV com o pandas
df = pd.read_csv(pacientes_geral, sep=';')


st.set_page_config(page_title = 'Dashboard de Análise de Dados', page_icon =":medical_symbol:", layout="wide")
df = pd.read_csv(pacientes_geral)
#%%
print("Colunas do DataFrame:", df.columns.tolist())
print("hello")
@st.cache_data
def load_data():
    # Leitura do arquivo CSV
    df = pd.read_csv(pacientes_geral)

    # Leitura do arquivo Excel
    municipios_df = pd.read_excel(excel_path)

    # Agrupar pelo IBGE
    count_by_ibge = df.groupby('IBGE')['index'].nunique().reset_index()


    # Contar casos por ano
    casos_por_ano = df.groupby('Ano').size().reset_index(name='Casos')

    # Obter a lista de cidades únicas
    cidades = [str(cidade) for cidade in df['CIDADEH'].unique()]
    return df, count_by_ibge, casos_por_ano, cidades
#%%

def page_1():
    st.title(" :medical_symbol: Casos de Câncer no Estado de São Paulo (FOSP)")
    st.markdown('<style>div.block-container{padding-top:3rem;}</style>',unsafe_allow_html=True)

    # Carregar os dados
    df, count_by_ibge,  casos_por_ano, cidades = load_data()
    
    #Filtro de intervalo de datas
    df["DTDIAG"] = pd.to_datetime(df["DTDIAG"], errors='coerce')
    startDate = pd.to_datetime(df["DTDIAG"]).min()
    endDate = pd.to_datetime(df["DTDIAG"]).max()

    col4, col5 = st.columns(2)
    with col4:
        date1 = st.date_input("Data Ínicio do Intervalo", value=startDate, min_value=startDate, max_value=endDate)

    with col5:
        date2 = st.date_input("Data Fim do Intervalo", value=endDate, min_value=startDate, max_value=endDate)

          # Converter date1 e date2 para datetime
    date1 = pd.to_datetime(date1)
    date2 = pd.to_datetime(date2)
    df = df[(df["DTDIAG"] >= date1) & (df["DTDIAG"] <= date2)].copy()

         # Verificação inicial dos dados de DTDIAG (fora do contexto do Streamlit)
    print("Colunas do DataFrame:", df.columns)
    print("Tipo de dados da coluna 'DTDIAG':", df["DTDIAG"].dtype)
    print("Data mínima em 'DTDIAG':", df["DTDIAG"].min())
    print("Data máxima em 'DTDIAG':", df["DTDIAG"].max())

        # Filtro para selecionar DRS na barra lateral com checkboxes
    st.sidebar.header('Escolha o DRS e Cidade')
    DRS = st.sidebar.multiselect("DRS", df["DRS"].unique())
    if not DRS:
        df2 = df.copy()
    else:
        df2 = df[df["DRS"].isin(DRS)]

    # Filtro para Municipio
    municipio = st.sidebar.multiselect("Cidade", df2["CIDADEH"].unique())
    if not municipio:
        df3 = df2.copy()
    else:
        df3 = df2[df2["CIDADEH"].isin(municipio)]

    # Filtro para Tipo de Câncer
    st.sidebar.header('Escolha o Tipo de Câncer')
    tipo_cancer = st.sidebar.multiselect("Tipo de Câncer", df3["TIPO_CANCER"].unique())
    if not tipo_cancer:
        df_filtered = df3.copy()  # Se nenhum tipo de câncer for selecionado, mantém df3
    else:
        df_filtered = df3[df3["TIPO_CANCER"].isin(tipo_cancer)]  # Aplica o filtro de TIPO_CANCER

    
    # Contadores de casos e por sexo
    total_casos = len(df_filtered)
    total_homens = len(df_filtered[df_filtered['SEXO'] == 1])
    total_mulheres = len(df_filtered[df_filtered['SEXO'] == 2])

    # Exibir métricas no topo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Casos", total_casos)
    with col2:
        st.metric("Homens", total_homens)
    with col3:
        st.metric("Mulheres", total_mulheres)

    # Conferindo se os códigos IBGE no DataFrame estão em formato inteiro
    count_by_ibge['IBGE'] = count_by_ibge['IBGE'].astype(int)

    # Carregar GeoJSON e garantir que o ID esteja em formato inteiro
    with urlopen('https://raw.githubusercontent.com/tbrugz/geodata-br/c39dfb040bfd466fe2a476bafed00749c5c42f16/geojson/geojs-35-mun.json') as response:
        geo_json = json.load(response)

    # Copiar o geo_json e adicionar contagens
    geo_json_with_counts = geo_json.copy()
    for feature in geo_json_with_counts['features']:
        ibge_code = int(feature['properties']['id'])  # Garantir que o código esteja como inteiro
        count = count_by_ibge[count_by_ibge['IBGE'] == ibge_code]['index'].values
        # Se houver contagem, atribui; caso contrário, coloca 0
        feature['properties']['index'] = int(count[0]) if len(count) > 0 else 0


    # Criação do mapa base
    mapa_sp = folium.Map(
        location=[-22.07, -48.4336],
        tiles="cartodbpositron",
        zoom_start=6.5
    )

    # Adicionar mapa Choropleth
    folium.Choropleth(
        geo_data=geo_json_with_counts,
        data=count_by_ibge,
        columns=["IBGE", "index"],
        key_on="properties.id",
        fill_color="GnBu",
        fill_opacity=0.9,
        line_opacity=0.5,
        legend_name="Contagem de Pacientes",
        nan_fill_color="white",
        name="Dados"
    ).add_to(mapa_sp)

    # Adicionar camada de destaque com tooltip atualizado
    highlight = folium.GeoJson(
        data=geo_json_with_counts,
        style_function=lambda x: {"fillColor": "white", "color": "black", "fillOpacity": 0.0001, "weight": 0.001},
        highlight_function=lambda x: {"fillColor": "darkblue", "color": "black", "fillOpacitxy": 0.5, "weight": 1},
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "index"],  # Certifique-se de que esses campos existam no GeoJSON
            aliases=["Cidade", "Número de Pacientes"],
            localize=True
        ),
        name="Destaque"
    )

    # Adicionar camada de destaque e controle de camadas ao mapa
    mapa_sp.add_child(highlight)
    folium.LayerControl().add_to(mapa_sp)

    # Exibir o mapa no Streamlit
    #folium_static(mapa_sp)

    # Contando a quantidade de ocorrências para cada valor na coluna 'Habilitação'
    contagem_habilitacao = df_filtered['Habilitação'].value_counts().reset_index()

    # Renomeando as colunas para tornar o gráfico mais legível
    contagem_habilitacao.columns = ['Habilitação', 'Quantidade']

    # Criando o gráfico de rosca
    fig = px.pie(contagem_habilitacao,
                names='Habilitação',  # As habilitações serão os segmentos
                values='Quantidade',  # As quantidades de pacientes para cada habilitação
                title='Quantidade de Pacientes por Habilitação',
                color='Habilitação',  # Cor distinta para cada habilitação
                color_discrete_sequence=px.colors.qualitative.Set3,  # Definindo a paleta de cores
                hole=0.5)  # Faz o gráfico virar uma rosca
    # ajustando o grafico
    fig.update_traces(textinfo='label+percent')

    # Removendo a legenda
    fig.update_layout(
        showlegend=False,  # Desabilita a legenda
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da área ao redor do gráfico transparente
    )

    # Base    


    # Ajustar os valores de 'SEXO' para nomes mais legíveis
    df_filtered['SEXO_NOME'] = df_filtered['SEXO'].map({1: 'Homem', 2: 'Mulher'})

    casos_por_ano_sexo = df_filtered.groupby(['Ano', 'SEXO_NOME']).size().reset_index(name='Casos')

    fig_bar = px.bar(
        casos_por_ano_sexo,
        x='Ano',
        y='Casos',
        color='SEXO_NOME',
        barmode='stack',
        labels={'SEXO_NOME': 'Sexo', 'Casos': 'Número de Casos', 'Ano': 'Ano'},
        color_discrete_map={'Homem': 'darkblue', 'Mulher': '#D62728'}  # Azul escuro e vermelho
    )

    #st.plotly_chart(fig_bar)

      # Exibição lado a lado das visualizações usando colunas

    #st.subheader("Mapa de São Paulo")
    #folium_static(mapa_sp, width = 800, height = 500)  

    # Definindo as faixas de ano de 3 em 3 anos
    bins = list(range(2000, 2024, 3))  # Gera os anos de 3 em 3, até 2023
    labels = [f"{i}-{i+2}" for i in range(2000, 2021, 3)]  # Gera as labels, ex: '2000-2002', '2003-2005', ...

    # Criando uma nova coluna 'Faixa_Ano' no df_filtered para armazenar as faixas de ano
    df_filtered['Faixa_Ano'] = pd.cut(df_filtered['Ano'], bins=bins, labels=labels, right=True)


    # Gerando a tabela de frequências com as faixas de ano nas linhas e 'Tipo_Diag' nas colunas
    tabela = pd.crosstab(df_filtered['Faixa_Ano'], df_filtered['Tipo_Diag'])

    # Convertendo para percentuais por faixa de ano
    tabela_percentual = tabela.div(tabela.sum(axis=1), axis=0) * 100

    # Exibindo a tabela de percentuais no Streamlit
    #st.write("Tabela de Percentuais de Tipo de Diagnóstico por Faixas de Ano")

    # Exibindo o mapa e a tabela ao lado
    col6, col7 = st.columns(2)
    with col6:
        st.subheader('Evolução dos Casos por Ano e Sexo')
        st.plotly_chart(fig_bar)
    with col7:
        st.subheader('Mapa de São Paulo')
        folium_static(mapa_sp, width=600, height=500) 
    
    # Mostrar as primeiras linhas do DataFrame filtrado
    #st.subheader('Dados dos Pacientes (Filtrados)')
    #st.write(df_filtered.head())    

    # Gráfico Tornado com base na faixa etária e sexo

    # Criar uma nova coluna 'SEXO_NOME' para facilitar a leitura
    df_filtered['SEXO_NOME'] = df_filtered['SEXO'].map({1: 'Homem', 2: 'Mulher'})

    # Agrupar por faixa etária e sexo
    tornado_data = df_filtered.groupby(['FAIXAETARIA', 'SEXO_NOME']).size().unstack(fill_value=0)

    # Criar um novo DataFrame para o gráfico
    tornado_data_plot = tornado_data.reset_index()
    tornado_data_plot = tornado_data_plot.melt(id_vars='FAIXAETARIA', value_vars=['Homem', 'Mulher'], var_name='SEXO', value_name='CONTAGEM')

    # Modificar os valores da contagem para mulheres para que apareçam à esquerda
    tornado_data_plot['CONTAGEM'] = tornado_data_plot.apply(lambda x: -x['CONTAGEM'] if x['SEXO'] == 'Mulher' else x['CONTAGEM'], axis=1)

    # Criar o gráfico tornado
    fig_tornado = px.bar(
        tornado_data_plot,  # DataFrame para o gráfico
        x='CONTAGEM',  # Contagem como eixo X
        y='FAIXAETARIA',  # Faixa etária como eixo Y
        color='SEXO',  # Usar o sexo para colorir as barras
        orientation='h',  # Horizontal
        labels={'CONTAGEM': 'Número de Casos', 'FAIXAETARIA': 'Faixa Etária'},
        text='CONTAGEM',  # Exibir contagem como texto nas barras
        color_discrete_map={'Homem': 'darkblue', 'Mulher': '#D62728'}  # Mapeamento de cores
    )

    # Atualizar o layout para melhor visualização
    fig_tornado.update_layout(barmode='overlay', xaxis_title='Número de Casos', yaxis_title='Faixa Etária')

    # Agrupar e contar os registros por TIPO_CANCER
    cancer_counts = df_filtered['TIPO_CANCER'].value_counts().reset_index()
    cancer_counts.columns = ['Tipo de Câncer', 'Frequência']

    # Adicionar uma coluna para ordenar, colocando 'Outros' por último
    cancer_counts['Ordem'] = cancer_counts['Tipo de Câncer'].apply(
        lambda x: 1 if x == 'Outros' else 0
    )

    # Ordenar primeiro pela 'Ordem' (garantindo que 'Outros' seja último) e depois pela 'Frequência'
    cancer_counts = cancer_counts.sort_values(
        by=['Ordem', 'Frequência'], ascending=[True, False]
    ).drop('Ordem', axis=1)

    # Criando o gráfico de barras vertical
    fig_tipo_cancer = px.bar(
        cancer_counts,
        x='Tipo de Câncer',
        y='Frequência',
        labels={'Tipo de Câncer': 'Tipo de Câncer', 'Frequência': 'Quantidade de Registros'},
        text='Frequência'
    )


    col10, col11 = st.columns(2)
    with col10:
        st.subheader('Faixa Etária')
        st.plotly_chart(fig_tornado) 
    with col11:
        st.subheader('Tipos de Câncer')
        st.plotly_chart(fig_tipo_cancer) 

# Página 2: Nova função
def page_2():
    st.title("Gestão de Dados")
    # Adicione aqui o conteúdo para a nova página
        # Exibir o mapa no Streamlit
    #folium_static(mapa_sp)

    # Carregar os dados
    df, count_by_ibge, casos_por_ano, cidades = load_data()
    
    #Filtro de intervalo de datas
    df["DTDIAG"] = pd.to_datetime(df["DTDIAG"], errors='coerce')
    startDate = pd.to_datetime(df["DTDIAG"]).min()
    endDate = pd.to_datetime(df["DTDIAG"]).max()

    col4, col5 = st.columns(2)
    with col4:
        date1 = st.date_input("Data Ínicio do Intervalo", value=startDate, min_value=startDate, max_value=endDate)

    with col5:
        date2 = st.date_input("Data Fim do Intervalo", value=endDate, min_value=startDate, max_value=endDate)

          # Converter date1 e date2 para datetime
    date1 = pd.to_datetime(date1)
    date2 = pd.to_datetime(date2)
    df = df[(df["DTDIAG"] >= date1) & (df["DTDIAG"] <= date2)].copy()

         # Verificação inicial dos dados de DTDIAG (fora do contexto do Streamlit)
    print("Colunas do DataFrame:", df.columns)
    print("Tipo de dados da coluna 'DTDIAG':", df["DTDIAG"].dtype)
    print("Data mínima em 'DTDIAG':", df["DTDIAG"].min())
    print("Data máxima em 'DTDIAG':", df["DTDIAG"].max())

    # Filtro para selecionar DRS na barra lateral com checkboxes
    st.sidebar.header('Escolha o DRS e Cidade')
    DRS = st.sidebar.multiselect("DRS", df["DRS"].unique())
    if not DRS:
        df2 = df.copy()
    else:
        df2 = df[df["DRS"].isin(DRS)]

    # Filtro para Municipio
    municipio = st.sidebar.multiselect("Cidade", df2["CIDADEH"].unique())
    if not municipio:
        df3 = df2.copy()
    else:
        df3 = df2[df2["CIDADEH"].isin(municipio)]

    # Filtro para Tipo de Câncer
    st.sidebar.header('Escolha o Tipo de Câncer')
    tipo_cancer = st.sidebar.multiselect("Tipo de Câncer", df3["TIPO_CANCER"].unique())
    if not tipo_cancer:
        df_filtered = df3.copy()  # Se nenhum tipo de câncer for selecionado, mantém df3
    else:
        df_filtered = df3[df3["TIPO_CANCER"].isin(tipo_cancer)]  # Aplica o filtro de TIPO_CANCER


    contagem_habilitacao = df_filtered['Habilitação'].value_counts().reset_index()

    # Renomeando as colunas para tornar o gráfico mais legível
    contagem_habilitacao.columns = ['Habilitação', 'Quantidade']
    fig = px.pie(contagem_habilitacao,
                names='Habilitação',  # As habilitações serão os segmentos
                values='Quantidade',  # As quantidades de pacientes para cada habilitação
                title='Quantidade de Pacientes por Habilitação',
                color='Habilitação',  # Cor distinta para cada habilitação
                color_discrete_sequence=px.colors.qualitative.Set3,  # Definindo a paleta de cores
                hole=0.5)  # Faz o gráfico virar uma rosca
    # ajustando o grafico
    fig.update_traces(textinfo='label+percent')

    # Removendo a legenda
    fig.update_layout(
        showlegend=False,  # Desabilita a legenda
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da área ao redor do gráfico transparente
    )

    # Definindo as faixas de ano de 3 em 3 anos
    bins = list(range(2000, 2024, 3))  # Gera os anos de 3 em 3, até 2023
    labels = [f"{i}-{i+2}" for i in range(2000, 2021, 3)]  # Gera as labels, ex: '2000-2002', '2003-2005', ...

    # Criando uma nova coluna 'Faixa_Ano' no df_filtered para armazenar as faixas de ano
    df_filtered['Faixa_Ano'] = pd.cut(df_filtered['Ano'], bins=bins, labels=labels, right=True)


    # Gerando a tabela de frequências com as faixas de ano nas linhas e 'Tipo_Diag' nas colunas
    tabela = pd.crosstab(df_filtered['Faixa_Ano'], df_filtered['Tipo_Diag'])

    # Convertendo para percentuais por faixa de ano
    
    tabela_percentual = tabela.div(tabela.sum(axis=1), axis=0) * 100
    col8, col9 = st.columns(2)
    with col8:
        st.plotly_chart(fig)

    with col9:
        st.subheader('Tipo de Diagnóstico')
        st.table(tabela_percentual)  # Exibindo a tabela de percentuais

    # Calcular a frequência de cada especialidade
    especialidades_freq = df_filtered['ESPECIALIDADE'].value_counts(normalize=True).reset_index()
    especialidades_freq.columns = ['Especialidade', 'Frequência']

    # Identificar quais especialidades têm menos de 10% do total
    especialidades_freq['Frequência (%)'] = especialidades_freq['Frequência'] * 100
    especialidades_menores = especialidades_freq[especialidades_freq['Frequência (%)'] < 1]['Especialidade']

    # Substituir especialidades menores por 'Demais Especialidades'
    df_filtered['ESPECIALIDADE_AGRUPADA'] = df_filtered['ESPECIALIDADE'].apply(
        lambda x: 'Demais Especialidades' if x in especialidades_menores.values else x
    )

    # Recalcular a frequência com as especialidades agrupadas
    especialidades_agrupadas_freq = df_filtered['ESPECIALIDADE_AGRUPADA'].value_counts().reset_index()
    especialidades_agrupadas_freq.columns = ['Especialidade', 'Frequência']

    # Ordenar as especialidades garantindo que 'Demais Especialidades' seja a última
    especialidades_agrupadas_freq['Ordem'] = especialidades_agrupadas_freq['Especialidade'].apply(
        lambda x: 1 if x == 'Demais Especialidades' else 0
    )
    especialidades_agrupadas_freq = especialidades_agrupadas_freq.sort_values(
        by=['Ordem', 'Frequência'], ascending=[True, False]
    ).drop('Ordem', axis=1)

    # Gráfico de barras das especialidades mais frequentes
    st.subheader('Especialidades Mais Frequentes')
    # Criar o gráfico de barras com as especialidades agrupadas
    fig_especialidade = px.bar(
        especialidades_agrupadas_freq,
        x='Especialidade',
        y='Frequência',
        title='Especialidades Mais Frequentes',
        labels={'Especialidade': 'Especialidade', 'Frequência': 'Frequência'},
        text='Frequência'
    )

    fig_especialidade.update_layout(xaxis_tickangle=-45)  # Rotacionar rótulos no eixo X
    st.plotly_chart(fig_especialidade)

def page_3():
    st.title("Curva de Sobrevivência")
    # Carregar os dados
    df, count_by_ibge, casos_por_ano, cidades = load_data()
    # Texto da lista
    texto = """
    Câncer de Boca e Orofaringe: C00-C14 (Inclui regiões como lábio, língua, gengiva, assoalho da boca, palato, glândulas salivares, amígdalas e faringe).
    Câncer de Esôfago e Estômago: C15-C16 (Esôfago e estômago).
    Câncer de Colorretal: C18-C20 (Cólon, junção retossigmoide e reto).
    Câncer de Fígado e Vias Biliares: C22-C24 (Fígado, vias biliares intra-hepáticas e vesícula biliar).
    Câncer de Pâncreas: C25 (Pâncreas).
    Câncer de Pulmão e Brônquios: C34 (Brônquios e pulmões).
    Câncer de Pele: C44 (Pele de várias partes do corpo).
    Câncer de Mama: C50 (Mama).
    Câncer. de Próstata: C61 (Próstata).
    """

    # Função para processar cada linha e retornar uma lista com as informações
    def processar_linha(linha):
        partes = linha.split(':')
        tipo_cancer = partes[0].strip()
        codigo_e_descricao = partes[1].split('(')
        codigo = codigo_e_descricao[0].strip()
        descricao = codigo_e_descricao[1].strip(')')
        return [tipo_cancer, codigo, descricao]

    # Separar as linhas e processar cada uma
    linhas = texto.strip().split('\n')
    dados = [processar_linha(linha) for linha in linhas]

    # Criar o DataFrameC
    df_tipos_cancer = pd.DataFrame(dados, columns=['tipo_cancer', 'codigo_tipo_range', 'descricao'])

    print(df_tipos_cancer)# Texto da lista
    texto = """
    Câncer de Boca e Orofaringe: C00-C14 (Inclui regiões como lábio, língua, gengiva, assoalho da boca, palato, glândulas salivares, amígdalas e faringe).
    Câncer de Esôfago e Estômago: C15-C16 (Esôfago e estômago).
    Câncer de Colorretal: C18-C20 (Cólon, junção retossigmoide e reto).
    Câncer de Fígado e Vias Biliares: C22-C24 (Fígado, vias biliares intra-hepáticas e vesícula biliar).
    Câncer de Pâncreas: C25 (Pâncreas).
    Câncer de Pulmão e Brônquios: C34 (Brônquios e pulmões).
    Câncer de Pele: C44 (Pele de várias partes do corpo).
    Câncer de Mama: C50 (Mama).
    Câncer. de Próstata: C61 (Próstata).
    """

    # Função para processar cada linha e retornar uma lista com as informações
    def processar_linha(linha):
        partes = linha.split(':')
        tipo_cancer = partes[0].strip()
        codigo_e_descricao = partes[1].split('(')
        codigo = codigo_e_descricao[0].strip()
        descricao = codigo_e_descricao[1].strip(')')
        return [tipo_cancer, codigo, descricao]

    # Separar as linhas e processar cada uma
    linhas = texto.strip().split('\n')
    dados = [processar_linha(linha) for linha in linhas]

    # Criar o DataFrameC
    df_tipos_cancer = pd.DataFrame(dados, columns=['tipo_cancer', 'codigo_tipo_range', 'descricao'])

    # gera lista de códigos a partir de um range
    #
    def criar_lista_codigos(codigo_inicial, codigo_final):
        prefixo = codigo_inicial[:1]  # 'C'
        numero_inicial = int(codigo_inicial[1:])  # '04' -> 4
        numero_final = int(codigo_final[1:])  # '07' -> 7

        lista_codigos = []
        for numero in range(numero_inicial, numero_final + 1):
            codigo = f"{prefixo}{numero:02}"
            lista_codigos.append(codigo)

        return lista_codigos

    # uso
    codigo_inicial = 'C04'
    codigo_final = 'C07'
    criar_lista_codigos(codigo_inicial, codigo_final)
    DRS = st.sidebar.multiselect("DRS", df["DRS"].unique())
    if not DRS:
        df2 = df.copy()
    else:
        df2 = df[df["DRS"].isin(DRS)]

    # Filtro para Municipio
    municipio = st.sidebar.multiselect("Cidade", df2["CIDADEH"].unique())
    if not municipio:
        df3 = df2.copy()
    else:
        df3 = df2[df2["CIDADEH"].isin(municipio)]

    # Filtro para Tipo de Câncer
    st.sidebar.header('Escolha o Tipo de Câncer')
    tipo_cancer = st.sidebar.multiselect("Tipo de Câncer", df3["TIPO_CANCER"].unique())
    if not tipo_cancer:
        df_filtered = df3.copy()  # Se nenhum tipo de câncer for selecionado, mantém df3
    else:
        df_filtered = df3[df3["TIPO_CANCER"].isin(tipo_cancer)]  # Aplica o filtro de TIPO_CANCER

    #
# seleção por codigos_tipo_cancer
#
    def select_data(df_filtered, codigos_tipo_cancer):
        """
        Realiza o pré-processamento do DataFrame, incluindo filtros e formatação de colunas.
        """
        df_aux = df_filtered.copy()

        # Filtro 1 - Topografia
        df_aux = df_aux[df_aux.TOPOGRUP.isin(codigos_tipo_cancer)]

        # Filtro 2 - Residentes de SP
        #df_aux = df_aux[df_aux.UFRESID == 'SP']

        # Filtro 3 - Casos com confirmação microscópica
        df_aux = df_aux[df_aux.BASEDIAG == 3]

        # Filtro 4 - Casos com morfologia 81403
        df_aux = df_aux[df_aux.MORFO == 81403]

        # Filtro 5 - ANODIAG até 2019
        df_aux = df_aux[df_aux.ANODIAG < 2020]

        # Converter as colunas de data para o formato datetime
        list_datas = ['DTDIAG', 'DTTRAT', 'DTULTINFO']
        for col_data in list_datas:
            df_aux[col_data] = pd.to_datetime(df_aux[col_data])

        # Calcular a diferença entre as datas para criar novas variáveis
        df_aux['ULTIDIAG'] = (df_aux.DTULTINFO - df_aux.DTDIAG).dt.days

        return df_aux
    
    #
    # ajuste dos dados para a análise de sobrevivência
    #
    def ajustes_para_KaplanMeier(df_filtered):
        df_aux = df_filtered.copy()
        df_aux = df_aux.reset_index(drop=True)

        # Eliminação de casos onde ULTIDIAG é menor que zero
        df_aux = df_aux[df_aux.ULTIDIAG >= 0]

        # Conversão de 'ULTIDIAG' para meses
        df_aux['time'] = (df_aux['ULTIDIAG'] / 30).round()

        # Ajuste da coluna 'ULTINFO' para ser binária (1 = morte / 0 = vivo)
        df_aux['event'] = df_aux['ULTINFO'].apply(lambda x: 1 if x in [3, 4] else 0)

        # Remoção de colunas desnecessárias
        df_aux = df_aux.drop(['ULTIDIAG', 'ULTINFO'], axis=1)

        return df_aux
    
    def gera_curvas_com_tabelas(df_filtered, df_tipos_cancer):
        st.header("Curvas Kaplan-Meier")

        tipos_cancer = df_tipos_cancer['tipo_cancer'].unique()
        colunas_por_linha = 3  # Quantos gráficos por linha

        # Itera pelos tipos de câncer em grupos de 3
        for i in range(0, len(tipos_cancer), colunas_por_linha):
            cols = st.columns(colunas_por_linha)
            for j, tipo in enumerate(tipos_cancer[i:i + colunas_por_linha]):
                with cols[j]:  # Coluna específica para o gráfico
                    codigos_tipo_range = df_tipos_cancer[df_tipos_cancer['tipo_cancer'] == tipo]['codigo_tipo_range'].values[0].split('-')
                    if len(codigos_tipo_range) > 1:
                        codigos_tipo_cancer = criar_lista_codigos(codigos_tipo_range[0], codigos_tipo_range[1])
                    else:
                        codigos_tipo_cancer = [codigos_tipo_range[0]]

                    # Filtra os dados para o tipo de câncer
                    df_aux = select_data(df_filtered, codigos_tipo_cancer).copy()
                    df_aux = ajustes_para_KaplanMeier(df_aux)

                    if df_aux.empty:
                        st.warning(f"Sem dados suficientes para o tipo de câncer: {tipo}")
                        continue

                    # Cria e ajusta o modelo Kaplan-Meier
                    kmf = KaplanMeierFitter()
                    kmf.fit(df_aux['time'], df_aux['event'], label=tipo)

                    # Criação do gráfico com tabela de risco
                    fig, ax = plt.subplots(figsize=(4, 4))  # Ajusta o tamanho
                    kmf.plot_survival_function(ax=ax, ci_show=True, color='blue', alpha=0.8)

                    # Adiciona tabela de risco
                    #add_at_risk_counts(kmf, ax=ax)

                    # Configurações do gráfico
                    ax.set_title(f"{tipo}", weight="bold", fontsize=10)
                    ax.set_xlabel("Meses", fontsize=8)
                    ax.set_ylabel("Prob. de Sobrevivência", fontsize=8)
                    ax.legend(loc="best", fontsize=6)

                    # Exibe o gráfico e a tabela no Streamlit
                    st.pyplot(fig)
    

    # Chamada da função para exibir os gráficos e tabelas
    gera_curvas_com_tabelas(df_filtered, df_tipos_cancer)

# Função para exportar página como PDF
    def export_page_as_pdf(html_content, file_name):
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
        }
        pdfkit.from_string(html_content, file_name, options=options)

    # Adicionar botão para exportar como PDF
    if st.button("Salvar como PDF"):
        # Captura o conteúdo renderizado da página
        st_html = st.get_report_ctx().html  # Obter o HTML atual
        export_page_as_pdf(st_html, f"{page_3.replace(' ', '_').lower()}.pdf")
        st.success("PDF gerado com sucesso!")
    
    # Função principal
def main():
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Escolha a Página:", ["Visão Geral", "Gestão de Dados", "Curva de Sobrevivência"])

    if page == "Visão Geral":
        page_1()
    elif page == "Gestão de Dados":
        page_2()
    elif page == "Curva de Sobrevivência":
        page_3()

# Executa a aplicação
if __name__ == "__main__":
    main()
