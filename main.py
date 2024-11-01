import streamlit as st
import base64

# Carregar a imagem da logo
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()
    return encoded_img

# Logo
logo_path = "img/logoRKP.png"
encoded_logo = get_base64_encoded_image(logo_path)

# Adicionar a logo ao topo do menu lateral
st.markdown(
    f"""
    <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded_logo}");
            background-size: 75px; 
            background-repeat: no-repeat;
            background-position: 28px 64px; /* 32px à esquerda e 64px abaixo do topo */
            padding-top: 120px; /* Compensar a altura da logo para que o conteúdo comece abaixo dela */
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# Criar as páginas necessárias
#Consultivo
consultivo = st.Page(
    "consultivo/consultivo.py", 
    title="Proposta Consultivo", 
    icon="⚖️", 
    default=True
)

consultivo_v2 = st.Page(
    "consultivo/consultivo_valor_por_autacao_profissional.py",
    title='consultivo',
    icon="⚖️"
)
#Contencioso
contencioso_proposta = st.Page(
    "contencioso/contencioso-proposta.py", 
    title="Proposta/Contrato Contencioso", 
    icon="⚖️"
)
consultivo_contencioso = st.Page(
    "consultivo_contencioso/consultivo-contencioso.py", 
    title="Proposta Consultivo e Contencioso",
    icon="⚖️"
)

#especial - proteção patrimonial
especial = st.Page(
    "Especial/especial.py", 
    title="Proposta - Reorganização Patrimonial", 
    icon="⚖️"
)

# Adicionar páginas ao menu de navegação
navigation_dict = {
    "Consultivo": [consultivo, consultivo_v2, consultivo_contencioso], #consultivo, 
    "Contencioso": [contencioso_proposta],# contencioso_contrato],
    "Especial": [especial]
}

pg = st.navigation(navigation_dict, position="sidebar")
pg.run()
