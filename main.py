import streamlit as st
import google.auth.transport.requests
import google.oauth2.id_token
from google_auth_oauthlib.flow import Flow
import os
import json

# # Configure os detalhes do cliente OAuth
# CLIENT_SECRETS_FILE = "client_secret.json"  # Nome do arquivo com as credenciais
# SCOPES = ["openid", "email", "profile"]
# REDIRECT_URI = "http://localhost:8501/"

# # Função para carregar as credenciais do cliente OAuth
# def load_credentials():
#     with open(CLIENT_SECRETS_FILE) as f:
#         return json.load(f)

# # Função para verificar o email do usuário
# def verify_email(email, allowed_domain):
#     domain = email.split('@')[-1]
#     return domain == allowed_domain

# # Função para iniciar o fluxo OAuth
# def initiate_flow():
#     credentials = load_credentials()
#     flow = Flow.from_client_config(
#         credentials,
#         scopes=SCOPES
#     )
#     flow.redirect_uri = REDIRECT_URI
#     auth_url, state = flow.authorization_url(prompt='consent')
#     return auth_url, flow

# # Função para obter o token do usuário
# def get_token(flow, code):
#     flow.fetch_token(code=code)
#     credentials = flow.credentials
#     return credentials.id_token

# # Página principal do aplicativo Streamlit
# def main():
#     st.title("Google OAuth Login")

#     # URL para iniciar o fluxo OAuth
#     auth_url, flow = initiate_flow()

#     # Mostrar botão de login
#     if st.button("Login with Google"):
#         st.markdown(f'<a href="{auth_url}" target="_self">Login with Google</a>', unsafe_allow_html=True)

#     # Verificar se o código de autorização está presente
#     if "code" in st.query_params:
#         code = st.query_params["code"][0]
#         id_token = get_token(flow, code)

#         # Verificar o email do usuário
#         request = google.auth.transport.requests.Request()
#         idinfo = google.oauth2.id_token.verify_oauth2_token(id_token, request)
#         email = idinfo['email']
#         allowed_domain = "yourcompany.com"

#         if verify_email(email, allowed_domain):
#             st.success(f"Bem-vindo, {email}")
#             # Continue com o restante do seu aplicativo
#         else:
#             st.error("Acesso negado. Apenas emails da organização são permitidos.")

# if __name__ == "__main__":
#     main()



# import streamlit as st
# import google.auth.transport.requests
# import google.oauth2.id_token
# from google_auth_oauthlib.flow import Flow
# import os
# import json
# from urllib.parse import urlparse, parse_qs

# # Configure os detalhes do cliente OAuth
# CLIENT_SECRETS_FILE = "client_secret.json"  # Nome do arquivo com as credenciais
# SCOPES = ["openid", "email", "profile"]
# REDIRECT_URI = "http://localhost:8501/"  # Certifique-se de que este URI está configurado no Google Cloud Console

# # Função para carregar as credenciais do cliente OAuth
# def load_credentials():
#     with open(CLIENT_SECRETS_FILE) as f:
#         return json.load(f)

# # Função para verificar o email do usuário
# def verify_email(email, allowed_domain):
#     domain = email.split('@')[-1]
#     return domain == allowed_domain

# # Função para iniciar o fluxo OAuth
# def initiate_flow():
#     credentials = load_credentials()
#     flow = Flow.from_client_config(
#         credentials,
#         scopes=SCOPES
#     )
#     flow.redirect_uri = REDIRECT_URI
#     auth_url, state = flow.authorization_url(prompt='consent')
#     return auth_url, flow

# # Função para obter o token do usuário
# def get_token(flow, code):
#     flow.fetch_token(code=code)
#     credentials = flow.credentials
#     return credentials.id_token

# # Página principal do aplicativo Streamlit
# def main():
#     st.title("Google OAuth Login")

#     # URL para iniciar o fluxo OAuth
#     auth_url, flow = initiate_flow()

#     # Mostrar botão de login
#     if st.button("Login with Google"):
#         st.markdown(f'<a href="{auth_url}" target="_self">Login with Google</a>', unsafe_allow_html=True)

#     # Verificar se o código de autorização está presente
#     query_params = st.query_params
#     if "code" in query_params:
#         code = query_params["code"][0]
#         st.write(f"Authorization code: {code}")

#         try:
#             id_token = get_token(flow, code)
#             st.write(f"ID Token: {id_token}")
#             # Verificar o email do usuário
#             request = google.auth.transport.requests.Request()
#             idinfo = google.oauth2.id_token.verify_oauth2_token(id_token, request)
#             email = idinfo['email']
#             allowed_domain = "yourcompany.com"

#             if verify_email(email, allowed_domain):
#                 st.success(f"Bem-vindo, {email}")
#                 # Continue com o restante do seu aplicativo
#             else:
#                 st.error("Acesso negado. Apenas emails da organização são permitidos.")
#         except Exception as e:
#             st.error(f"Erro ao obter o token: {e}")

# if __name__ == "__main__":
#     main()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

consultivo = st.Page(
    ".\consultivo\consultivo.py", 
    title="Proposta Consultivo", 
    icon="💪", 
    default=True
    )
contencioso_proposta = st.Page(
    ".\contencioso\contencioso-proposta.py", 
    title="Proposta Contencioso", 
    icon="💪"
    )
contencioso_contrato = st.Page(
    ".\contencioso\contencioso-contrato-preenchido.py", 
    title='Contrato preenchido', 
    icon="💪"
    )
consultivo_contencioso = st.Page(
    ".\consultivo_contencioso\consultivo-contencioso.py", 
    title="Proposta Consultivo e Contencioso",
    icon="💪"
    )
especial = st.Page(
    ".\Especial\especial.py", 
    title="Proposta - Proteção Patrimonial", 
    icon="💪"
    )
# pg = st.navigation(
#     {
#         "Consultivo": [consultivo, consultivo_contencioso],
#         "Contencioso": [contencioso_proposta, contencioso_contrato],
#         "Especial": [especial]
#     }
# )
if st.session_state.logged_in:
    pg = st.navigation(
      {
        "Consultivo": [consultivo, consultivo_contencioso],
        "Contencioso": [contencioso_proposta, contencioso_contrato],
        "Especial": [especial],
        "Account": [logout_page],
    }
)
else:
    pg = st.navigation([login_page])

pg.run()