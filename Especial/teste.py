import streamlit as st
import pandas as pd
import re
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread_dataframe import set_with_dataframe

# Configurar as credenciais do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/credentials.json', scope)
client = gspread.authorize(creds)

# Nome da planilha e aba onde os dados serão salvos
spreadsheet_name = "nome_da_planilha"
worksheet_name = "cliente"

# Conectar-se à planilha
sheet = client.open(spreadsheet_name)

# Interface do Streamlit
st.title("Salvar Dados no Google Sheets")

# Supondo que você tenha os dados do formulário já definidos
nome_cliente = "Cliente Exemplo"
input_contencioso_objeto = "Objeto Exemplo"
instancia_ = "Instancia Exemplo"
orgao_ = "Orgão Exemplo"
itens_atuacao = "Itens Exemplo"
prolabore_inicial_formatado = "60000.00"
parcelamento = "Regular"
numero_parcelas_formatado = "12"
valor_entrada_formatado = "10000.00"
parcelamento_restante = "50000.00"
valor_parcelamento_formatado = "4166.67"
prolabore_manutencao = "Manutenção Exemplo"
prolabore_manutencao_valor = "5000.00"
tipo_exito = "Exito Exemplo"
exito_percentual_formatado = "10.00"
exito_outro_texto = "Exito Outro Texto Exemplo"
valor_teto_exito_formatado = "100000.00"
expectativa_tempo = "6 meses"

if st.button('Salvar'):
    novo_dado = {
        'nome_cliente': nome_cliente,
        'objeto_contencioso': input_contencioso_objeto,
        'instancia_superior': instancia_,
        'orgao': orgao_,
        'itens_atuacao': itens_atuacao,
        'pro_labore_inicial': prolabore_inicial_formatado,
        'parcelamento': parcelamento,
        'numero_parcelas_formatado': numero_parcelas_formatado,
        'valor_entrada': valor_entrada_formatado,
        'parcelamento_restante': parcelamento_restante,
        'valor_parcelamento_formatado': valor_parcelamento_formatado,
        'pro_labore_manutencao': prolabore_manutencao,
        'pro_labore_manutencao_valor_sm': prolabore_manutencao_valor,
        'tipo_exito': tipo_exito,
        'exito_percentual_formatado': exito_percentual_formatado,
        'exito_texto': exito_outro_texto,
        'exito_valor_teto': valor_teto_exito_formatado,
        'tempo_expectativa': expectativa_tempo,
    }
    
    # Criar um DataFrame com os novos dados
    df_novo_dado = pd.DataFrame([novo_dado])

    # Nome da nova aba na planilha
    worksheet_title = re.sub(r'[^\w\s]', '_', nome_cliente)
    
    # Criar uma nova aba com o nome do cliente
    new_worksheet = sheet.add_worksheet(title=worksheet_title, rows=len(df_novo_dado), cols=len(df_novo_dado.columns))
    
    # Adicionar os dados na nova aba
    set_with_dataframe(new_worksheet, df_novo_dado)
    
    st.success('Dados salvos com sucesso!')
