#%%
import pandas as pd
import json
import numpy as np
from urllib.request import urlopen
import numpy as np



# Caminho para os arquivos
pacientes_geral = r"C:\Users\ferre\Downloads\RHC_SP_2000_2024_GERAL\pacigeral.csv"
excel_path = "G:\Meu Drive\Iniciação Científica\RELATORIO_DTB_BRASIL_MUNICIPIO.xlsx"

# Leitura do arquivo CSV
df = pd.read_csv(pacientes_geral)
# Lista de colunas a serem removidas
colunas_para_remover = [
    'UFNASC', 'UFRESID', 'DTCONSULT', 'DESCTOPO', 'ECGRUP', 'T', 'N', 'M', 'S', 'G', 
    'LOCALTNM', 'IDMITOTIC', 'PSA', 'META01', 'META02', 'META03', 'META04', 'TRATFANTES', 
    'TRATFAPOS', 'NENHUM', 'CIRURGIA', 'RADIO', 'QUIMIO', 'HORMONIO', 'TMO', 'IMUNO', 
    'OUTROS', 'NENHUMANT', 'CIRURANT', 'RADIOANT', 'QUIMIOANT', 'HORMOANT', 'TMOANT', 
    'IMUNOANT', 'OUTROANT', 'NENHUMAPOS', 'CIRURAPOS', 'RADIOAPOS', 'QUIMIOAPOS', 
    'HORMOAPOS', 'TMOAPOS', 'IMUNOAPOS', 'OUTROAPOS', 'FAIXAETAR', 'LATERALI', 'REC01', 
    'REC02', 'REC03', 'REC04'
]

# Remover as colunas do DataFrame
df = df.drop(columns=colunas_para_remover)

# Verificar as colunas restantes
print(df.columns)

# Leitura do arquivo Excel
municipios_df = pd.read_excel(excel_path)

# Renomear as colunas para facilitar a junção
municipios_df.rename(columns={
    'Nome_Município': 'CIDADEH', 'Código Município Completo': 'IBGE'}, inplace=True)

# Renomear a coluna para harmonizar com a base anterior
df.rename(columns={
    'CIDADE_INS': 'CIDADEH'}, inplace=True)





# Realizar a junção com base no nome do município
#df = pd.merge(df, municipios_df[['CIDADEH', 'IBGE']], on='CIDADEH', how='left')

# Verificar se 'IBGE_y' foi criada e renomeá-la para 'IBGE'
#if 'IBGE_y' in df.columns:
#    df.rename(columns={'IBGE_y': 'IBGE'}, inplace=True)

# Resetar o índice
df = df.reset_index()



# Adicionar a coluna do ano para a evolução dos casos
df['DTDIAG'] = pd.to_datetime(df['DTDIAG'], errors='coerce')
df['Ano'] = df['DTDIAG'].dt.year


# Obter a lista de cidades únicas
cidades = [str(cidade) for cidade in df['CIDADEH'].unique()]

# Dicionário de mapeamento de números para especialidades
especialidades_dict = {
1: "ALERGIA/IMUNOLOGIA", 2: "CIRURGIA CARDIACA", 3: "CIRURGIA CABEÇA E PESCOÇO",
4: "CIRURGIA GERAL", 5: "CIRURGIA PEDIATRICA", 6: "CIRURGIA PLASTICA",
7: "CIRURGIA TORAXICA", 8: "CIRURGIA VASCULAR", 9: "CLINICA MEDICA",
10: "DERMATOLOGIA", 11: "ENDOCRINOLOGIA", 12: "GASTROCIRURGIA",
13: "GASTROENTEROLOGIA", 14: "GERIATRIA", 15: "GINECOLOGIA",
16: "GINECOLOGIA / OBSTETRICIA", 17: "HEMATOLOGIA", 18: "INFECTOLOGIA",
19: "NEFROLOGIA", 20: "NEUROCIRURGIA", 21: "NEUROLOGIA",
22: "OFTALMOLOGIA", 23: "ONCOLOGIA CIRURGICA", 24: "ONCOLOGIA CLINICA",
25: "ONCOLOGIA PEDIATRICA", 26: "ORTOPEDIA", 27: "OTORRINOLARINGOLOGIA",
28: "PEDIATRIA", 29: "PNEUMOLOGIA", 30: "PROCTOLOGIA",
31: "RADIOTERAPIA", 32: "UROLOGIA", 33: "MASTOLOGIA",
34: "ONCOLOGIA CUTANEA", 35: "CIRURGIA PELVICA", 36: "CIRURGIA ABDOMINAL",
37: "ODONTOLOGIA", 38: "TRANSPLANTE HEPATICO", 99: "IGNORADO"
}
# Adicionar uma nova coluna 'ESPECIALIDADE' usando o dicionário de mapeamento
df['ESPECIALIDADE'] = df['CLINICA'].map(especialidades_dict)

# Dicionário de mapeamento de números POR HABILITAÇÕES
habilit = {
1: "UNACON",
2: "UNACON exclusivo de Oncologia Pediátrica",
3: "CACON",
4: "Hospital Geral",
5: "Voluntários",
6: "Inativos"
}

# Adicionar uma nova coluna 'Habilitação' usando o dicionário de mapeamento
df['Habilitação'] = df['HABILIT2'].map(habilit)

# Dicionário Diagnóstico
metodo_diagnostico = {
1: "EXAME CLINICO",
2: "RECURSOS AUXILIARES NÃO MICROSCÓPICOS",
3: "CONFIRMAÇÃO MICROSCÓPICA",
4: "SEM INFORMAÇÃO"
}
    # Adicionar uma nova coluna 'Tipo_Diag' usando o dicionário de mapeamento
df['Tipo_Diag'] = df['BASEDIAG'].map(metodo_diagnostico)

# Convertendo a coluna 'IDADE' para numérico, forçando erros a NaN
df['IDADE'] = pd.to_numeric(df['IDADE'], errors='coerce')

# Definindo as faixas etárias
def definir_faixa_etaria(idade):
    if idade < 0:
        return 'Idade Inválida'
    elif idade < 18:
        return '0-17 anos'
    elif 18 <= idade < 30:
        return '18-29 anos'
    elif 30 <= idade < 50:
        return '30-49 anos'
    elif 50 <= idade < 65:
        return '50-64 anos'
    else:
        return '65 anos ou mais'

# Aplicando a função para criar a nova coluna 'FAIXAETARIA'
df['FAIXAETARIA'] = df['IDADE'].apply(definir_faixa_etaria)
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

# Função para processar cada linha do texto
def processar_linha(linha):
    partes = linha.split(':')
    tipo_cancer = partes[0].strip()
    codigo_e_descricao = partes[1].split('(')
    codigo = codigo_e_descricao[0].strip()
    descricao = codigo_e_descricao[1].strip(')')
    return [tipo_cancer, codigo, descricao]

# Criar o DataFrame com os tipos de câncer
linhas = texto.strip().split('\n')
dados = [processar_linha(linha) for linha in linhas]
df_tipos_cancer = pd.DataFrame(dados, columns=['tipo_cancer', 'codigo_tipo_range', 'descricao'])

# Função para verificar se o código está dentro de um intervalo
def categorizar_cancer(codigo):
    for _, row in df_tipos_cancer.iterrows():
        codigo_range = row['codigo_tipo_range']
        if '-' in codigo_range:
            inicio, fim = codigo_range.split('-')
            if inicio <= codigo <= fim:
                return row['tipo_cancer']
        elif codigo == codigo_range:
            return row['tipo_cancer']
    return 'Outros'

#Aplicar a função ao DataFrame principal
df['TIPO_CANCER'] = df['TOPOGRUP'].apply(categorizar_cancer)

# Definir os nomes dos hospitais
hospitais = ['Hospital A', 'Hospital B', 'Hospital C', 'Hospital D', 'Hospital E']

# Atribuir aleatoriamente um hospital a cada linha do DataFrame
df['NOME_HOSPITAL'] = np.random.choice(hospitais, size=len(df))

# Verificar se a coluna foi criada corretamente
print(df[['NOME_HOSPITAL']].head())
# Exibir o resultado
print(df.columns)
df.to_csv(r'G:\Meu Drive\Iniciação Científica\pacigeral_12_23_transformed_2024.csv', index=False, encoding='utf-8')
