#%%
# Libraties 
import pandas as pd 
import re 
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image 
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores',page_icon='🚚',layout='wide')

#------------------------------------
# Funções
#-------------------------------------

def clean_code(df1):
    """ Está função tem a responsabilidade de limparo dataframe
    
    Tipos de limpeza: 
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto da variavel númerica)

    input: Dataframe
    output: Dataframe Tratado
    """

    # Filtrando dataframe considerando a coluna Delivery_person_Age com valores difentes de 'NaN '
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # Convertendo tipo da coluna object para "int"
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # Covertendo a coluna Rating para Float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Convertendo a coluna Order_Date de texto para Data
    df1['Order_Date']= pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')

    # Covertendo multiple_deliveries de texto para numero inteiro (int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Removendo os espaços dentro de strings/textos/objects
    df1.loc[:, 'ID']= df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density']= df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order']= df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle']= df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival']= df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City']= df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival']= df1.loc[:, 'Festival'].str.strip()

    # limpando a coluna de time taken 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1]) 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def top_delivers(df1,top_asc):
    df1 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID'])
            .max().sort_values(['City','Time_taken(min)'], ascending = top_asc)
            .reset_index())

    df_aux1 = df1.loc[df1['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df1.loc[df1['City'] =='Urban', :].head(10)
    df_aux3 = df1.loc[df1['City'] =='Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop=True)
    
    return df3

#----------------------- Inicio da Estrutura lógica do Código----------------------------
# import dataset
#-----------------------
df = pd.read_csv('dataset/train.csv')


#-----------------------
# Limpando os dados
#-----------------------
df1 = clean_code(df)



#===========================================
# Layout - Streamlit
# https://streamlit.io/
    # Comando para rodar no terminal (streamlit run <nome_arquivo.py>)
    # Comando para matar o processo CTRL+C
#===========================================

#===========================================
# Barra Lateral
#===========================================

st.header('Marketplace - Visão Entregadores')

#image_path = r'D:\Files\Comunidade_DS\portfolio_projetos\ftc_prog_python\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
        'Até qual valor ?',
        value=pd.datetime(2022,4,13),
        min_value = pd.datetime(2022,2,11),
        max_value= pd.datetime(2022,4,6),
        format = 'DD-MM-YYYY')


st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condiçoes do transito',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Luciano B da Silva')

#Filtro de data na pagina
linhas_selecionadas = df1['Order_Date']<date_slider
df1 = df1.loc[linhas_selecionadas,:]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]


#===========================================
# Layout - Streamlit
#===========================================

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1: 
    with st.container():

        #Header
        st.title('# Overall Metrics')
        col1, col2, col3, col4 = st.columns(4,gap='large')
        with col1:
            # A Maior Idade dos Entregadores
            maior_idade= df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior de Idade',maior_idade)
        
        with col2:
             # A Maior Idade dos Entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min() 
            col2.metric('Menor de Idade',menor_idade)

        with col3:
            # Melhor condição de veiculos
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição de veiculos',melhor_condicao)
            # Pior condição de veiculos
        with col4:
            #st.subheader('Pior condição de Veiculos')
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição de Veiculos',pior_condicao) 


    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Avaliação Medias por Entregador')
            df_avg_ratings_per_deliver = (df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index() )
            st.dataframe(df_avg_ratings_per_deliver)

        with col2: 
            st.markdown('##### Avaliação Medias por Transito')
            df_avg__std_rating_by_traffic = (df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                              .groupby('Road_traffic_density')
                                              .agg({'Delivery_person_Ratings': ['mean','std'] } ) ) 

            # mudar de nome das colunas 
            df_avg__std_rating_by_traffic.columns = ['delivery_mean','delivery_std']

            # reset do index 
            df_avg__std_rating_by_traffic = df_avg__std_rating_by_traffic.reset_index()
            st.dataframe(df_avg__std_rating_by_traffic)

            st.markdown('##### Avaliação Medias por Clima')
            df_avg__std_rating_by_weather = (df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                                .groupby('Weatherconditions')
                                                .agg({'Delivery_person_Ratings': ['mean','std'] } ) )

            # mudar de nome das colunas     
            df_avg__std_rating_by_weather.columns = ['delivery_mean','delivery_std']

            # reset do index 
            df_avg__std_rating_by_weather = df_avg__std_rating_by_weather.reset_index()
            st.dataframe(df_avg__std_rating_by_weather)



    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Top Entregadores mais rapidos')
            df3 = top_delivers(df1, top_asc = True)
            st.dataframe(df3)
            
        with col2: 
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3) 

            
                   








# %%
