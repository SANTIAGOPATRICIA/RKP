import streamlit as st
# from streamlit_google_auth import Authenticate

# authenticator = Authenticate(
#     secret_credentials_path='client_secret.json',
#     cookie_name='my_cookie_name',
#     cookie_key='this_is_secret',
#     redirect_uri='http://localhost:8501',
# )

# # Initialize session state
# if 'connected' not in st.session_state:
#     st.session_state['connected'] = False

# if 'user_info' not in st.session_state:
#     st.session_state['user_info'] = {}

# # Check if the user is already authenticated
# authenticator.check_authentification()

# # Display the login button if the user is not authenticated
# authenticator.login()

# # Display the user information and logout button if the user is authenticated
# if st.session_state['connected']:
#     # login = st.image(st.session_state['user_info'].get('picture'))
#     # st.write(f"Hello, {st.session_state['user_info'].get('name')}")
#     # st.write(f"Your email is {st.session_state['user_info'].get('email')}")
    
#     # Criar as páginas necessárias
#     consultivo = st.Page(
#         ".\consultivo\consultivo.py", 
#         title="Proposta Consultivo", 
#         icon="💪", 
#         default=True
#     )
#     contencioso_proposta = st.Page(
#         ".\contencioso\contencioso-proposta.py", 
#         title="Proposta Contencioso", 
#         icon="💪"
#     )
#     contencioso_contrato = st.Page(
#         ".\contencioso\contencioso-contrato-preenchido.py", 
#         title='Contrato preenchido', 
#         icon="💪"
#     )
#     consultivo_contencioso = st.Page(
#         ".\consultivo_contencioso\consultivo-contencioso.py", 
#         title="Proposta Consultivo e Contencioso",
#         icon="💪"
#     )
#     especial = st.Page(
#         ".\Especial\especial.py", 
#         title="Proposta - Proteção Patrimonial", 
#         icon="💪"
#     )

#     # Criar uma página para logout
#     def logout_page():
#         st.write("Você está prestes a sair do aplicativo.")
#         if st.button('Log out'):
#             authenticator.logout()
    
#     logout = st.Page(
#         logout_page,
#         title="Log out",
#         icon="🚪"
#     )

#     # Adicionar páginas ao menu de navegação
#     pg = st.navigation(
#         {
#             "Consultivo": [consultivo, consultivo_contencioso],
#             "Contencioso": [contencioso_proposta, contencioso_contrato],
#             "Especial": [especial],
#             "Sair": [logout]  # Adiciona a opção de logout como a última opção
#         }
#     )

#     pg.run()
# else:
#     st.write("Por favor, faça login para acessar o aplicativo.")





# Criar as páginas necessárias
consultivo = st.Page(
    "consultivo/consultivo.py", 
    title="Proposta Consultivo", 
    icon="💪", 
    default=True
)
contencioso_proposta = st.Page(
    "contencioso/contencioso-proposta.py", 
    title="Proposta Contencioso", 
    icon="💪"
)
contencioso_contrato = st.Page(
    "contencioso/contencioso-contrato-preenchido.py", 
    title='Contrato preenchido', 
    icon="💪"
)
consultivo_contencioso = st.Page(
    "consultivo_contencioso/consultivo-contencioso.py", 
    title="Proposta Consultivo e Contencioso",
    icon="💪"
)
especial = st.Page(
    "Especial/especial.py", 
    title="Proposta - Proteção Patrimonial", 
    icon="💪"
)

# Adicionar páginas ao menu de navegação
pg = st.navigation(
    {
        "Consultivo": [consultivo, consultivo_contencioso],
        "Contencioso": [contencioso_proposta, contencioso_contrato],
        "Especial": [especial],
        "Sair": [logout]  # Adiciona a opção de logout como a última opção
    }
)

pg.run()
