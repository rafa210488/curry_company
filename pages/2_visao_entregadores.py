# Importando as libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Bibliotecas necessárias
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', layout='wide')


# =============================================
# Funções
# =============================================

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
    
        Tipos de Limpeza:
        1. Remoção dos dados Nan
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    
    """
    # 1 - Convertendo a coluna Age de texto para número
    linhas_selecionadas = (df1["Delivery_person_Age"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1["Road_traffic_density"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1["City"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1["Festival"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)
    
    
    # 2 - Convertendo a coluna Ratings de texto para número decimal (float)
    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)
    
    # 3 - Convertendo a coluna order_date de texto para data
    df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format="%d-%m-%Y")
    
    # 4 - Convertendo multiple_deliveries de texto para número inteiro (int)
    linhas_selecionadas = (df1["multiple_deliveries"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)
    
    # 5 - Removendo os espaços dentro de strings/texto/object
    # df1 = df1.reset_index(drop=True)
    # for i in range(len(df1)):
    #   df1.loc[i, "ID"] = df1.loc[i, "ID"].strip()
    
    # 6 - Removendo os espaços dentro de strings/texto/object
    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()
    df1.loc[:, "Festival"] = df1.loc[:, "Festival"].str.strip()
    
    # 7 - Limpando a coluna de Time Taken
    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply( lambda x: x.split('(min) ')[1])
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)

    return df1

def top_delivers(df1, top_asc):
    df2 = df1.loc[:, ["Delivery_person_ID", "Time_taken(min)", "City"]].groupby(["City", "Delivery_person_ID"]).mean().sort_values(["City","Time_taken(min)"], ascending=top_asc).reset_index()

    df_aux01 = df2.loc[df2["City"] == "Metropolitian", :].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban", :].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban", :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3

# ===================== Inicio da Estrutura Lógica=====================================
# =====================================================================================

# Importando o dataset
# ================================================================
df = pd.read_csv('train.csv')

# ===========================================================================
# Limpeza dos Dados
# ===========================================================================
df1 = clean_code(df)


# =========================================
# Barra Lateral
# =========================================

st.markdown('# Marketplace - Visão Entregadores')


image= Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma Data Limite')
date_slider = st.sidebar.slider('Até qual valor?', value=datetime(2022, 4, 13), min_value=datetime(2022, 2, 11), max_value=datetime(2022, 4, 6), format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) 
df1 = df1.loc[linhas_selecionadas, :]


# ======================================================
# Layout no Streamlit
# ======================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown('# Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # maior idade dos entregadores
            maior_idade = df1["Delivery_person_Age"].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            # menor idade dos entregadores
            menor_idade = df1["Delivery_person_Age"].min()
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            # melhor condição de veículos
            melhor_condicao = df1["Vehicle_condition"].max()
            col3.metric('Melhor Condição', melhor_condicao)
            
        with col4:
            # pior condição de veículos
            pior_condicao = df1["Vehicle_condition"].min()
            col4.metric('Pior Condição', pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.markdown('# Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliação média por entregador')
            df_avg_ratings_per_deliver = df1.loc[:, ["Delivery_person_ID", "Delivery_person_Ratings"]].groupby(["Delivery_person_ID"]).mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
        
        with col2:
            st.subheader('Avaliação média por trânsito')
            df_avg_std_rating_by_traffic = df1.loc[:, ["Delivery_person_Ratings", "Road_traffic_density"]].groupby(["Road_traffic_density"]).agg({"Delivery_person_Ratings": ["mean", "std"]})
            # mudança de nome das colunas
            df_avg_std_rating_by_traffic.columns = ["delivery_mean", "delivery_std"]
            # reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            
            st.subheader('Avaliação média por clima')
            df_avg_std_weather = df1.loc[:, ["Delivery_person_Ratings", "Weatherconditions"]].groupby(["Weatherconditions"]).agg({"Delivery_person_Ratings" : ["mean", "std"]})
            df_avg_std_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_weather = df_avg_std_weather.reset_index()
            st.dataframe(df_avg_std_weather)
    

    with st.container():
        st.markdown('# Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.subheader('Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
        

    
