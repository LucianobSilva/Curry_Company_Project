import streamlit as st 
from PIL import Image 

st.set_page_config(
    page_title="Home",
    page_icon="📊",
    layout= 'wide'
)

#image_path = r'D:\Files\Comunidade_DS\portfolio_projetos\ftc_prog_python\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=130)


st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencia: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de cresciemento.
        - VIsão Geográfica: Insights de g   eolocalizão.
    - Visão Entregador: 
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    """)