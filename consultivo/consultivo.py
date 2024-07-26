import pandas as pd
import numpy as np
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from st_pages import add_indentation
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime
import locale
import time
from num2words import num2words
import os
from tempfile import NamedTemporaryFile
from utils.funcoes import format_paragraph, add_formatted_text, format_title_centered, \
    format_title_justified, num_extenso, data_extenso, fonte_name_and_size, add_section,\
    create_paragraph, atualizar_base_dados, num_extenso_percentual, set_table_borders


st.set_page_config(layout="wide")


# Define o local para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error as e:
    print(f"Erro ao definir a localidade: {e}")


add_indentation() 
# Expande a largura da tela

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.horizontal = False

#####################################################################################

lista_numerada = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)', 'j)', 'k)', 'l)', 'm)', 'n)', 'o)', 'p)', 'q)', 'r)', 's)', 't)']

#####################################################################################
dados, desenvolvimento = st.columns([2,3])

# Dicionário das informações
perguntas_respostas = {}

with dados:
    st.write('**Informação para a proposta**')
    
    # Conectar ao Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    existing_data = conn.read(worksheet="cliente", ttls=5, usecols=[1])
    lista_clientes = existing_data.sort_values(by='Nome')['Nome'].unique().tolist()
    
    # Adiciona uma opção para cadastrar novo cliente
    lista_clientes.append("--Novo cliente--")
    lista_clientes = sorted(lista_clientes)

    nome_cliente = st.selectbox(
        'Cliente',
        (lista_clientes),
        index=None,
        placeholder='Selecione o cliente'
    )
    
    if nome_cliente == '--Novo cliente--':
        with st.form('Novo Cliente'):
            novo_cliente = st.text_input('Cadastrar novo cliente')
            submitted = st.form_submit_button("Cadastrar")
            if submitted and novo_cliente:
                # Atualizar a lista de clientes
                if novo_cliente not in lista_clientes:
                    lista_clientes.insert(-1, novo_cliente)
                    st.selectbox('Cliente', lista_clientes, index=lista_clientes.index(novo_cliente))
    
    st.divider()
    # Objeto da proposta
    input_objeto = st.text_area(label="Objeto(s) da proposta (ENTER para quebra de linha)")
    resumo_objeto = st.text_area(label="Resumo do(s) objeto(s) (ENTER para quebra de linha)")

    perguntas_respostas = {
        'nome_cliente': nome_cliente,
        '[objeto_texto]': input_objeto,
        '[resumo_objeto]': resumo_objeto,
    }

    # Resumo do objeto da proposta
    df_inputs = pd.DataFrame(columns=[
        'objeto', 
        'total-de-horas', 
        'valor-aplicado', 
        'valor-formatado',
        'valor_por_extenso',
        'subtotal',
        'subtotal-extenso'
    ])
    
    atuacao = perguntas_respostas['[resumo_objeto]'].split("\n")
    textos_paragrafos = []
    texto_padrao = []
    hora_total_objeto = []
    valor_total_proposta = []
    if len(atuacao) > 1:
        st.markdown('**Preencher para cada objeto**')
        for p in atuacao:
            st.write(f'**{p}**')
            hora_total = st.number_input(label='Total de horas:', step=10, key=f'hora_total_{p}')
            hora_total = int(hora_total)
            hora_total_objeto.append(hora_total)
            valor_aplicado = st.selectbox("Valor aplicado",
                (1150.00, 850.00, 680.00, 580.00, 490.00, 290.00), key=f'valor_aplicado_{p}')
            valor_formatado = "{:.2f}".format(round(valor_aplicado, 2))
            valor_por_extenso = num_extenso(valor_formatado)
            valor_total = (hora_total * valor_aplicado)
            valor_total_formatado = "{:.2f}".format(round(valor_total, 2))
            subtotal_extenso = num_extenso(valor_total_formatado)
            st.write(f'*Subtotal R${valor_total}*')
            valor_total_proposta.append(valor_total)
            df_inputs = df_inputs.append(
                {
                    'objeto': p,
                    'total-de-horas': hora_total,
                    'valor-aplicado': valor_aplicado,
                    'valor_por_extenso': valor_por_extenso,
                    'valor-formatado': valor_por_extenso,
                    'subtotal': valor_total,
                    'subtotal-extenso': subtotal_extenso
                }, ignore_index=True
            )
    else:
        hora_total = st.number_input(label='Total de horas:', step=10, key='hora_total')
        hora_total = int(hora_total)
        hora_total_objeto.append(hora_total)
        valor_aplicado = st.selectbox("Valor aplicado",
            (1150.00, 850.00, 680.00, 580.00, 490.00, 290.00), key='valor_aplicado')
        valor_formatado = "{:.2f}".format(round(valor_aplicado, 2))
        valor_por_extenso = num_extenso(valor_formatado)
        valor_total = (hora_total * valor_aplicado)
        valor_total_formatado = "{:.2f}".format(round(valor_total, 2))
        subtotal_extenso = num_extenso(valor_total_formatado)
        st.write(f'**Total R${valor_total}**')
        valor_total_proposta.append(valor_total)
        df_inputs = df_inputs.append(
            {
                'objeto': atuacao[0] if atuacao else '',
                'total-de-horas': hora_total,
                'valor-aplicado': valor_aplicado,
                'valor_por_extenso': valor_por_extenso,
                'valor-formatado': valor_formatado,
                'subtotal': valor_total,
                'subtotal-extenso': subtotal_extenso
            }, ignore_index=True
        )
    
    valor_proposto = sum(valor_total_proposta)
    st.write(f'**Valor da proposta: R${valor_proposto}**')
    
    st.divider()
    desconto = st.number_input('Percentual do desconto do consultivo (%)', min_value=0.0, max_value=100.0, key='consultivo_desc')
    desconto_percentual = float("{:.2f}".format(desconto))
    desconto_percentual_formatado = "{:.2f}".format(round(desconto, 2))

    total_final = 0.0
    if desconto > 0.0:
        total_final = valor_proposto * ((100.00 - desconto_percentual) / 100)
        total_final_formatado = "{:.2f}".format(round(total_final, 2))
    else:
        total_final = valor_proposto
        total_final_formatado = "{:.2f}".format(round(total_final, 2))

    st.write(f"Valor da proposta com desconto: R${total_final_formatado}")
    st.divider()    
    parcelar = st.radio('Parcelar o valor?', ['Sim', 'Não'],
        key='parcelar',
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        horizontal=st.session_state.horizontal,
        index=None)

    parcelamento = 1.0  # Se não for parcelado, será pago em uma única vez

    if parcelar == 'Sim':
        parcelamento = st.selectbox('Parcelamento do valor proposto', (2, 3, 4, 5, 6))
        valor_parcelado = total_final / parcelamento
        valor_parcelado_formatado = "{:.2f}".format(round(valor_parcelado, 2))
        st.write(f'O valor parcelado da proposta é de R${valor_parcelado_formatado}')

    perguntas_respostas = {
        'nome_cliente': nome_cliente,
        '[objeto_texto]': input_objeto,
        '[resumo_objeto]': resumo_objeto,
        '[hora_total]': hora_total,
        '[valor_aplicado]': valor_aplicado,
        '[valor_total]': valor_proposto,
        '[desconto]': desconto,
        '[desconto_percentual]': desconto_percentual,
        '[total_final]': total_final
    }

# Processar o cadastro do novo cliente

if nome_cliente == '--Novo cliente--' and submitted and novo_cliente:
    conn.write({
        'worksheet': 'cliente',
        'data': {
            'Nome': novo_cliente
        }
    })

# Gerar o documento Word com base nos dados fornecidos
if st.button('Gerar Documento'):
    documento = Document()
    format_title_centered(documento, 'Proposta Comercial', 'Title', 1, 14)

    p = create_paragraph(documento, '1. Cliente:', 'ListBullet')
    add_formatted_text(p, nome_cliente, 'ListBullet')

    p = create_paragraph(documento, '2. Objeto(s) da Proposta:', 'ListBullet')
    add_formatted_text(p, input_objeto, 'ListBullet')

    if desconto > 0:
        p = create_paragraph(documento, f'Desconto aplicado: {desconto}%', 'ListBullet')
    p = create_paragraph(documento, f'Valor total da proposta: R${total_final_formatado}', 'ListBullet')

    if parcelar == 'Sim':
        p = create_paragraph(documento, f'Parcelamento: {parcelamento} vezes', 'ListBullet')

    # Salvar documento em arquivo temporário e permitir download
    with NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        documento.save(tmp_file.name)
        st.download_button(
            label="Baixar Documento",
            data=open(tmp_file.name, 'rb').read(),
            file_name='proposta_comercial.docx',
            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
