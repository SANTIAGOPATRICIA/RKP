# import streamlit as st
# from st_pages import Page, Section, show_pages, add_page_title

# add_page_title()


# show_pages(
#     [
#         Section("consultivo", icon="🎈️"),
#         Page(".\consultivo\consultivo.py","Proposta consultivo", icon="💪", in_section=True),
#         Section("contencioso", icon="🎈️"),
#         Page(".\contencioso\contencioso-proposta.py", icon="💪", in_section=True),
#         Page(".\contencioso\contencioso-contrato.py", icon="💪", in_section=True),
#         Section("Consultivo e contencioso", icon="🎈️"), 
#         # Page(".\consultivo\modelo-consultivo-e-contencioso-propostas.py","Proposta consultivo e contencioso", icon="💪", in_section=True),
#         Page(".\consultivo_contencioso\consultivo-contencioso.py", "Consultivo e contencioso", icon="💪", in_section= True),
#         Section("Especial", icon="🎈️"),
#         Page(".\Especial\especial.py", "Proteção patrimonial", icon="💪", in_section=True)
#     ]
# )

import streamlit as st
# from st_pages import Page, Section, show_pages, add_page_title

# add_page_title()

# show_pages(
#     [
#         Section("Consultivo", icon="🎈"),
#         Page(".\consultivo\consultivo.py", "Proposta Consultivo", icon="💪", in_section=True),
#         Section("Contencioso", icon="🎈"),
#         Page(".\contencioso\contencioso-proposta.py", "Proposta Contencioso", icon="💪", in_section=True),
#         Page(".\contencioso\contencioso-contrato-preenchido.py", 'Contrato preenchido', in_section=True),
#         Page(".\contencioso\contencioso-contrato.py", "Contrato Contencioso", icon="💪", in_section=True),
#         Section("Consultivo e Contencioso", icon="🎈"),
#         Page(".\consultivo_contencioso\consultivo-contencioso.py", "Consultivo e Contencioso", icon="💪", in_section=True),
#         Section("Especial", icon="🎈"),
#         Page(".\Especial\especial.py", "Proteção Patrimonial", icon="💪", in_section=True)
#     ]
# )


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