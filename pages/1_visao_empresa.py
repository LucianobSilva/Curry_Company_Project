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

st.set_page_config(page_title='Visão Empresa',page_icon='📈',layout='wide')


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

#------------------------- Dashboards -------------------------------------------
def order_metric(df1):
        # Agrupando a quantidade de pedidos por dia
        df_aux = (df1.loc[:,['ID','Order_Date']].groupby('Order_Date')
                                                .count()
                                                .reset_index())
        # Renomeia a coluna de acordo com a ordem sequencial
        df_aux.columns = ['Order_Date', 'qtde_entregas']  
        # grafico de barras 
        fig = px.bar(df_aux, x='Order_Date', y='qtde_entregas')
        return fig

def traffic_order_share(df1):
    cols = ["ID","Road_traffic_density"]
    # agrupamento
    df_aux = (df1.loc[:,cols].groupby('Road_traffic_density')
                                .count()
                                .reset_index())
    
    df_aux['perc_ID'] = (df_aux['ID']/df_aux['ID'].sum())*100   
    
    # grafico 
    fig =px.pie(df_aux, values='perc_ID', names='Road_traffic_density')
    return fig

def traffic_order_city(df1):             
    cols = ['ID','City','Road_traffic_density']
    # agrupamento e calculo
    df_aux = (df1.loc[:,cols].groupby(['City','Road_traffic_density'])
                .count()
                .reset_index())
    
    df_aux['perc_ID'] = (df_aux['ID']/df_aux['ID'].sum())*100
    # grafico 
    fig = px.scatter (df_aux , x='City', y='Road_traffic_density', size ='ID', color='City')
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U") 
    # Na lista Cols =  Primeira a coluna que será a variavel calculo, depois as que faram parte do agrupamento . 
    df_aux = (df1.loc[:,['ID','week_of_year']].groupby('week_of_year')
                                              .count()
                                              .reset_index())
    # grafico
    fig = px.line(df_aux, x ='week_of_year', y='ID')
    return fig

def order_share_by_week(df1): 
    # agrupamento e calculos
    df_aux1 = (df1.loc[:, ['ID','week_of_year']].groupby('week_of_year')
                                                .count()
                                                .reset_index())
    df_aux2 = (df1.loc[:, ['Delivery_person_ID','week_of_year']].groupby('week_of_year')
                                                               .nunique()
                                                               .reset_index())
    # merge
    df_aux = pd.merge( df_aux1, df_aux2, how='inner',on ='week_of_year'  )
    # calculos final
    df_aux['order_by_delivery'] = (df_aux['ID'] / df_aux['Delivery_person_ID'])*100
    # grafico
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery') 
    return fig

def country_maps(df1):
    data_plot = (df1.loc[:,[
                            'City',
                            'Road_traffic_density',
                            'Delivery_location_latitude',
                            'Delivery_location_longitude']]
                            .groupby(['City', 'Road_traffic_density'])
                            .median()
                            .reset_index()) # Nota: Usado a médiana, a média causaria erro dado que calcularia a longitude e latitude 

    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )

    # for para iterar marcações no mapa. (Nota: Só funciona com iterrows)
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )

    folium_static(map_,width=1024,height=600)

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

st.header('Marketplace - Visão Cliente')

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
    default = ['Low','Medium','High','Jam'])

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

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visçao Tática','Visão Geográfica'])

with tab1: 
    with st.container():
        fig = order_metric(df1)
        st.markdown('# Orders by day')
        st.plotly_chart(fig,use_container_width=True)
   
    with st.container():
        col1,col2 =  st.columns(2)
       
        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            fig = traffic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig,use_container_width=True)

with tab2: 
    with st.container(): 
        fig = order_by_week(df1)
        st.markdown("# Order by Weeky")
        st.plotly_chart(fig,use_container_width=True)        
        
    with st.container():
        fig = order_share_by_week(df1)
        st.markdown("# Order Share by Weeky")
        st.plotly_chart(fig,use_container_width=True)         

with tab3: 
    st.markdown("# Country Maps")
    country_maps(df1)
 