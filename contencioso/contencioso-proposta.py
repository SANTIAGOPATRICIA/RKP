import pandas as pd
# import numpy as np
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from st_pages import add_indentation
import docx
from docx import Document
from docx.shared import Pt
from datetime import datetime
import locale
import time
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re
from num2words import num2words
from tempfile import NamedTemporaryFile
from utils.funcoes import format_paragraph, add_formatted_text, format_title_centered, \
    format_title_justified, num_extenso, data_extenso, fonte_name_and_size, add_section,\
    num_extenso_percentual, set_table_borders, obter_texto_parcelas

##########################################################

## listas necessárias

#Lista dos TJs
TJs = [
    'Tribunal de Justiça do Acre (TJAC)','Tribunal de Justiça de Alagoas (TJAL)',
    'Tribunal de Justiça do Amapá (TJAP)', 'Tribunal de Justiça do Amazonas (TJAM)',
    'Tribunal de Justiça da Bahia (TJBA)', 'Tribunal de Justiça do Ceará (TJCE)',
    'Tribunal de Justiça do Distrito Federal e Territórios (TJDFT)', 'Tribunal de Justiça do Espírito Santo (TJES)',
    'Tribunal de Justiça de Goiás (TJGO)', 'Tribunal de Justiça do Maranhão (TJMA)',
    'Tribunal de Justiça de Mato Grosso (TJMT)', 'Tribunal de Justiça de Mato Grosso do Sul (TJMS)',
    'Tribunal de Justiça de Minas Gerais (TJMG)', 'Tribunal de Justiça do Pará (TJPA)',
    'Tribunal de Justiça da Paraíba (TJPB)', 'Tribunal de Justiça do Paraná (TJPR)',
    'Tribunal de Justiça de Pernambuco (TJPE)', 'Tribunal de Justiça do Piauí (TJPI)',
    'Tribunal de Justiça do Rio de Janeiro (TJRJ)', 'Tribunal de Justiça do Rio Grande do Norte (TJRN)',
    'Tribunal de Justiça do Rio Grande do Sul (TJRS)', 'Tribunal de Justiça de Rondônia (TJRO)',
    'Tribunal de Justiça de Roraima (TJRR)', 'Tribunal de Justiça de Santa Catarina (TJSC)',
    'Tribunal de Justiça de São Paulo (TJSP)', 'Tribunal de Justiça de Sergipe (TJSE)',
    'Tribunal de Justiça do Tocantins (TJTO)'
    ]

#lista numerada para replace
lista_numerada = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)', 'j)', 'k)', 'l)', 'm)', 'n)', 'o)', 'p)', 'q)', 'r)', 's)', 't)']


############################################################
recuo = "&nbsp;" * 24


# st.set_page_config(layout="wide")

add_indentation()

# Define o local para português do Brasil
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# Carregar o CSV existente ou criar um novo DataFrame
try:
    df_inputs = pd.read_csv('df_inputs.csv')
except FileNotFoundError:
    df_inputs = pd.DataFrame(columns=['nome_cliente', 'objeto_contencioso', 'instancia_superior', 'orgao', 'itens_atuacao',
                                      'pro_labore_inicial', 'pro_labore_inicial_desconto','pro_labore_manutencao', 'pro_labore_manutencao_valor_sm',
                                      'exito', 'exito_valor_teto', 'tempo_expectativa'])


# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.horizontal = False

dados, desenvolvimento = st.columns([2, 3])

with dados:
    # st.table(df_inputs)
    st.write('**Informação proposta - contencioso**')

    #Carregando o arquvio do google sheets
    # conn = st.connection("gsheets", type=GSheetsConnection)
    # contencioso_data = conn.read(worksheet="bd-contencioso")

    # Carregando a lista de clientes pela primeira vez
    lista_clientes = pd.read_csv('clientes.csv')
    lista_clientes = lista_clientes.sort_values(by='Nome')['Nome'].unique().tolist()

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
        form = st.form('Novo Cliente')
        nome_cliente = form.text_input('Cadastrar novo cliente')
        form.form_submit_button("Cadastrar")
    lista_clientes.append(nome_cliente)

    st.divider()
    st.write("Objeto")
    input_contencioso_objeto = st.text_area(label=f"Conforme solicitação, apresentamos proposta de honorários para \
                                            atuação judicial, em defesa dos interesses de {nome_cliente}...")

    #Instancia
    instancia_ = st.selectbox("Instância", options=['primeira instância', 'segunda instância', 'tribunal superior'], index = None)
    if instancia_ == 'segunda instância':
        orgao_ = st.selectbox("Tribunal", options = TJs, index = None)
    elif instancia_ == 'tribunal superior':
        orgao_ = st.selectbox("Tribunal", options = ['STJ', "STF"], index = None)
    else:
        orgao_ = st.text_input(label = "Vara ou seção", placeholder = None)


    # Valores do contencioso
    st.divider()
    st.write('Pró-labore inicial')

    # Input para o valor do pro-labore inicial
    prolabore_inicial = st.number_input('Pró-labore inicial (R$)', key='prolabore_inicial')
    prolabore_inicial_formatado = "{:.2f}".format(round(prolabore_inicial, 2))

    #Parcelamento do prolabore inicial
    parcelamento = st.selectbox('Parcelamento', ['Regular', 'Entrada + parcelas'], index=None)

    numero_parcelas_formatado = ''
    valor_entrada_formatado = ''
    numero_parcelas = 0
    parcelamento_restante = 0

    if parcelamento != None:
        if parcelamento == 'Regular':
            numero_parcelas = st.selectbox('nº de parcelas', options=range(2,25))
            numero_parcelas_formatado = "{:.2f}".format(round(numero_parcelas, 2))
            valor_parcelamento = prolabore_inicial / numero_parcelas
            valor_parcelamento_formatado = "{:.2f}".format(round(valor_parcelamento, 2))
            st.write(f'O valor do parcelamento é de R$ {valor_parcelamento}')
        else:
            valor_entrada = st.number_input('Valor da entrada (R$)', min_value=1000)
            valor_entrada_formatado = "{:.2f}".format(round(valor_entrada, 2))
            saldo = prolabore_inicial - valor_entrada
            st.write(f'*O saldo é de R$ {saldo}*')
            parcelamento_restante = st.number_input('nº parcelas', min_value=2)
            # parcelamento_restante_formatado = "{.1f}".format(round(parcelamento_restante, 2))
            valor_parcelamento = saldo / parcelamento_restante
            valor_parcelamento_formatado = "{:.2f}".format(round(valor_parcelamento, 2))
            st.write(f'*O valor do parcelamento é de R$ {valor_parcelamento}*')
    
    # Selectbox para o tempo de isenção
    st.divider()
    st.write('Pró-labore de manutenção')
    prolabore_manutencao = st.selectbox("Tempo de isenção (meses)",
                                        (0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60),
                                        key='tempo_isencao')

    # Condicional para exibir o selectbox do pró-labore de manutenção
    prolabore_manutencao_valor = 0.0
    if prolabore_manutencao > 0:
        prolabore_manutencao_valor = st.selectbox("Proporção do salário mínimo para o pró-labore de manutenção",
                                                (0.5, 1, 1.5, 2, 2.5),
                                                key='valor_manutencao')


    # Input para o percentual do benefício econômico
    st.divider()
    st.write('Êxito')
    tipo_exito = st.selectbox('Tipo de êxito', options=['benefício econômico', 'outro'], key='exito', index=None)
    exito_percentual = 0.0
    exito_percentual_formatado = "0.00"
    exito_outro_texto = ""

    # if tipo_exito != None:
    if tipo_exito == 'benefício econômico':
        exito_percentual = st.number_input('Percentual do benefício econômico (%)', min_value=0.0, max_value=100.0, step=0.5, key='exito_percentual')
        exito_percentual_formatado = "{:.2f}".format(round(exito_percentual, 2))
    else:
        exito_percentual = st.number_input('Percentual (%)', min_value=0.0, max_value=100.0, step=0.5, key='exito_percentual')
        exito_percentual_formatado = "{:.2f}".format(round(exito_percentual, 2))
        exito_outro_texto = st.text_area('texto')

    # Input para o valor teto do êxito
    valor_teto_exito = st.number_input('Valor teto do êxito (R$)', key='valor_teto_exito')
    valor_teto_exito_formatado = "{:.2f}".format(round(valor_teto_exito, 2))

    #expectativa duração contrato
    st.divider()
    st.write('Estimativa duração do processo')
    expectativa_tempo = st.selectbox("Estimativa de duração do processo (meses)",
                                     (0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60),
                                     key='tempo_expectativa')


# #####################################################################################
# Abrir documento com papel timbrado da RKP
document = docx.Document(r".\docx\RKP-PapelTimbrado.docx")

# Definir fonte e tamanho do documento
fonte_name_and_size(document, 'Arial', 12)


# Adicionar uma sessão ao documento
section = add_section(document, 5,3,2,2)


# Data
data = datetime.now()
paragraph_date = document.add_paragraph(f'Brasília/DF, {data_extenso(data)}')
paragraph_format = paragraph_date.paragraph_format
paragraph_format.alignment = 2  # a direita


#############################################################################
# Adicionar título ao doc
title = document.add_heading('PROPOSTA PARA PRESTAÇÃO \nDE SERVIÇOS ADVOCATÍCIOS')
format_title_centered(title)
space_format = title.paragraph_format
space_format.space_before = Pt(48)


p_de = document.add_paragraph()
p_de.add_run('DE: ROQUE KHOURI & PINHEIRO ADVOGADOS ASSOCIADOS S/S').bold = True
p_de_format = p_de.paragraph_format
p_de_format.line_spacing = Pt(18)
p_de_format.space_before = Pt(148)
p_de_format.space_after = Pt(8)


paragraph_para = document.add_paragraph()
paragraph_para.add_run(f'PARA: {nome_cliente} (Interessado(a))').bold = True
paragraph_format = paragraph_para.paragraph_format
paragraph_format.line_spacing = Pt(18)
paragraph_format.space_after = Pt(48)

paragraph_ref = document.add_paragraph()
paragraph_ref.text = 'Referência: PROPOSTA DE HONORÁRIOS ADVOCATÍCIOS'
paragraph_format = paragraph_ref.paragraph_format
paragraph_format.space_before = Pt(18)
paragraph_format.space_after = Pt(96)
paragraph_format.line_spacing = Pt(18)



paragraph = document.add_paragraph()
format_paragraph(paragraph, 3, 1.5748,0, 48,16,20)
full_text= "ROQUE KHOURI & PINHEIRO ADVOGADOS ASSOCIADOS S/S, com sede no SIG - Quadra 01, Lote 495, Edifício Barão do Rio Branco, sala 244, Brasília-DF, CEP 70.610-410, telefones 3321-7043 e 3226-0137, inscrita no CNPJ sob o nº 03.899.920/0001- 81, registro na Ordem dos Advogados do Brasil – OAB/DF sob o número 616/00 – RS, endereço eletrônico www.khouriadvocacia.com.br, vem, mui respeitosamente, apresentar PROPOSTA DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS, nas condições a seguir."
# Texto que será negritado
bold_text = "ROQUE KHOURI & PINHEIRO ADVOGADOS ASSOCIADOS S/S"
# Adicionar o texto formatado ao parágrafo
add_formatted_text(paragraph, full_text, bold_text)

# I - DOS SERVIÇOS A SEREM DESENVOLVIDOS
title_one = document.add_heading('I - DOS SERVIÇOS A SEREM DESENVOLVIDOS', level=2)
format_title_justified(title_one)

#paragrafo objeto
paragraph_objeto = document.add_paragraph(f'Conforme solicitação, apresentamos proposta de honorários para atuação judicial, em defesa dos interesses de {nome_cliente} {orgao_} {input_contencioso_objeto}, para todo o acompanhamento junto ao poder judiciário, até o julgamento final em {instancia_}.')
format_paragraph(paragraph_objeto,3, 1.5748,0, 18,18,18)


#itens atuação
itens_atuacao = [
    "Providências preliminares de levantamento e análise de todas as informações e documentos relativos ao objeto da presente proposta, a fim de propiciar o embasamento jurídico necessário;",
    '',
    f"Atuação contenciosa com a confecção de petição inicial, ajuizamento de ação e acompanhamento de processo judicial até o seu julgamento final em sede de {instancia_};",
    f"Elaboração de todas as petições e recursos necessários (incluindo memoriais) ao acompanhamento da ação judicial até o seu julgamento final em sede de {instancia_};",
    "Diligências pessoais junto aos Tribunais, em especial despachos presenciais e telepresenciais com os Juízes, Desembargadores e Ministros responsáveis pelo julgamento, se cabível.",
    "Participações em reuniões com V.Sa. e demais profissionais envolvidos, incluindo em entendimentos entre as partes, se forem necessários;"
]


if instancia_ == 'segunda instância':
    itens_atuacao[1] += f'Acompanhamento do processo junto ao {orgao_}, até o julgamento final em {instancia_};'
else:
    del itens_atuacao[1]

# Cria uma nova lista com a mesma quantidade de elementos de `servicos`, preenchida com itens de `lista_numerada`
lista_numerada_servicos = lista_numerada[:len(itens_atuacao)]

# Serviços a serem prestados
for i in range(len(itens_atuacao)):
    paragrafo_ = document.add_paragraph(f'{lista_numerada[i]} {itens_atuacao[i]}')
    format_paragraph(paragrafo_, 3, 0, 1.5748, 18,18,18)


#paragrafo I-IV
paragraph_four = document.add_paragraph()
format_paragraph(paragraph_four,3, 1.5748, 0, 18,18,18)
paragraph_four.text ='Para o cumprimento dos serviços, o escritório disponibilizará sua equipe técnica, sendo que haverá advogado responsável pelo acompanhamento direto da demanda.'

#paragrafo I-V
paragraph_five = document.add_paragraph()
format_paragraph(paragraph_five,3, 1.5748,0, 18,18,18)
paragraph_five.text ='A Roque Khouri & Pinheiro Advogados Associados alerta que a análise e confecção de contrato é realizada com base no direito aplicável, jurisprudência atual e principalmente nas informações e documentos que serão sempre fornecidos pela Interessada.'

#############################################################################
# II - DA POLÍTICA GERAL DE VALORES - HONORÁRIOS
#titulo II
title_two = document.add_heading('II - DA POLÍTICA GERAL DE VALORES - HONORÁRIOS', level=2)
format_title_justified(title_two)
#Paragrafo II-I
paragraph_two_one = document.add_paragraph()
format_paragraph(paragraph_two_one,3, 1.5748, 0, 18,18,18)
paragraph_two_one.text = "Faz parte integrante de todas as nossas propostas de honorários os itens abaixo, componentes da nossa Política de Honorários de consultoria:" #\nTaxas horárias de honorários para projetos. Para projetos, nós cobramos valores de honorários de acordo com as seguintes taxas horárias:

#Paragrafo II-II
paragraph_two_two = document.add_paragraph()
format_paragraph(paragraph_two_two,3, 1.5748,0, 18,18,18)
full_text= "Taxas horárias de honorários para projetos. Para projetos, nós cobramos valores de honorários de acordo com as seguintes taxas horárias:"
# Texto que será negritado
bold_text = "Taxas horárias de honorários para projetos."
# Adicionar o texto formatado ao parágrafo
add_formatted_text(paragraph_two_two, full_text, bold_text)

# Adicionar tabela
table = document.add_table(rows=1, cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style =  None #'LightShading-Accent3'
# Definir bordas da tabela
set_table_borders(table)
# get table data -------------
items = (
    ('Sócio Majoritário - Dr. Paulo Roque', 'R$1.150,00'),
    ('Sócia Nominal - Dra. Ângela Pinheiro', 'R$850,00'),
    ('Advogado Sênior', 'R$680,00'),
    ('Advogado Pleno', 'R$580,00'),
    ('Advogado Júnior', 'R$490,00'),
    ('Paralegal/Estagiário', 'R$290,00')
)

# populate header row --------
heading_cells = table.rows[0].cells
heading_cells[0].text = 'Profissional'
heading_cells[1].text = 'Valor'


# Alinhar texto na primeira linha ao centro verticalmente
for cell in heading_cells:
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

# Definir cor de fundo para a primeira linha
shading_elm_0 = OxmlElement('w:shd')
shading_elm_0.set(qn('w:fill'), 'B4FF00')  # RGB (180, 255, 0)
heading_cells[0]._element.get_or_add_tcPr().append(shading_elm_0)
shading_elm_1 = OxmlElement('w:shd')
shading_elm_1.set(qn('w:fill'), 'B4FF00')  # RGB (180, 255, 0)
heading_cells[1]._element.get_or_add_tcPr().append(shading_elm_1)


# add a data row for each item
for item in items:
    cells = table.add_row().cells
    cells[0].text = item[0]
    cells[1].text = item[1]
    cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT  # Alinhar texto à direita na segunda coluna

# Definir bordas da tabela
set_table_borders(table)


#Paragrafo II-III
paragraph_two_three = document.add_paragraph()
format_paragraph(paragraph_two_three, 3, 1.5748,0, 18,18,18)
full_text= "Reembolso de Despesas. As despesas incorridas no desenvolvimento dos trabalhos, como, por exemplo, despesas com ligações telefônicas, correios, couriers e outros meios de envio de documentos, com impressão de cópias e digitalização de documentos, com taxas governamentais, com viagens, táxis e outros deslocamentos, e, se aplicável, despesas com custas processuais e outras despesas relativas a processos arbitrais, judiciais e administrativos, e honorários de advogados correspondentes, serão reembolsadas, mediante a apresentação de planilha discriminada, e, se solicitado, dos respectivos comprovantes. Nenhuma despesa superior a R$ 1.000,00 (um mil Reais) será incorrida sem sua prévia aprovação por escrito."
# Texto que será negritado
bold_text = "Reembolso de Despesas."
# Adicionar o texto formatado ao parágrafo
add_formatted_text(paragraph_two_three, full_text, bold_text)


#Paragrafo II-IV
paragraph_two_four = document.add_paragraph()
format_paragraph(paragraph_two_four, 3, 1.5748,0, 18,18,18)
full_text= "Interrupção ou Suspensão dos Trabalhos. Se por qualquer motivo os trabalhos forem eventualmente interrompidos ou suspensos, faremos o levantamento das horas trabalhadas e o valor de honorários pagos até então e, se houver saldo a ser pago, faremos o faturamento correspondente. Caso haja honorários a serem restituídos, a restituição será feita no mês seguinte ao da interrupção ou suspensão dos trabalhos e do valor a ser restituído serão descontados os tributos correspondentes pagos ou a pagar."
# Texto que será negritado
bold_text = "Interrupção ou Suspensão dos Trabalhos."
# Adicionar o texto formatado ao parágrafo
add_formatted_text(paragraph_two_four, full_text, bold_text)
#############################################################################

# III - DOS HONORÁRIOS ESPECÍFICOS
#titulo III
title_three = document.add_heading('III - DOS HONORÁRIOS ESPECÍFICOS', level=2)
format_title_justified(title_three)

# #paragrafo III-I
# paragraph_three_one = document.add_paragraph('Com o intuito de manter a proporcionalidade entre prestação de serviços e pagamento, os honorários advocatícios devidos em consequência da presente prestação de serviços seriam cobrados por meio do sistema de horas, ou seja, cada ato praticado, esse Jurídico seria remunerado de acordo com o tempo necessário para praticá-lo.')
# format_paragraph(paragraph_three_one, 3, 1.5748, 0,18,18,18)

paragraph_three_one_one = document.add_paragraph('Os honorários advocatícios devidos em consequência da prestação de serviços previstas no item I seriam assim determinados:')
format_paragraph(paragraph_three_one_one, 3, 1.5748, 0,18,18,18)

#concordancia nominal das parcelas
parcelas_texto = obter_texto_parcelas(numero_parcelas)
# Atualizar 'parcelas_texto' caso o parcelamento seja 'Entrada + parcelas'
if parcelamento == 'Entrada + parcelas':
    parcelas_texto = obter_texto_parcelas(parcelamento_restante)

# valor atuação contencioso
#pro-labore inicial
if parcelamento == None:
    valor_prolabore_inicial = document.add_paragraph(f'a) Pró-labore inicial mínimo: R$ {prolabore_inicial_formatado} ({num_extenso(prolabore_inicial_formatado)});')
    format_paragraph(valor_prolabore_inicial, 3, 0, 1.5748, 18, 18, 18)
elif parcelamento == 'Regular':
    valor_prolabore_inicial = document.add_paragraph(f'a) Pró-labore inicial mínimo: R$ {prolabore_inicial_formatado} ({num_extenso(prolabore_inicial_formatado)}), podendo ser divido em {parcelas_texto} mensais consecutivas de R$ {valor_parcelamento}, a ser paga na assinatura deste contrato;')
    format_paragraph(valor_prolabore_inicial, 3, 0, 1.5748, 18, 18, 18)
else:
    valor_prolabore_inicial = document.add_paragraph(f'a) Pró-labore inicial mínimo: R$ {prolabore_inicial_formatado} ({num_extenso(prolabore_inicial_formatado)}), sendo a primeira parcela no valor de R$ {valor_entrada_formatado} ({num_extenso(valor_entrada_formatado)}) a ser paga na assinatura deste contrato, e {parcelas_texto} mensais consecutivas no valor de R$ {valor_parcelamento_formatado} ({num_extenso(valor_parcelamento_formatado)});')
    format_paragraph(valor_prolabore_inicial, 3, 0, 1.5748, 18, 18, 18)


# pro-labore de manutenção
if prolabore_manutencao == 0:
    valor_honorario_manutencao = document.add_paragraph(f"b) Honorário de manutenção: Isento.")
    format_paragraph(valor_honorario_manutencao, 3, 0, 1.5748, 18,18,18)
else:
    valor_honorario_manutencao = document.add_paragraph(f"b) Honorário de manutenção: Isento durante o período de {prolabore_manutencao} meses. Após este período, se o processo perdurar, será devido o valor de {prolabore_manutencao_valor} salário mínimo mensal;")
    format_paragraph(valor_honorario_manutencao, 3, 0, 1.5748, 18,18,18)

#exito
if tipo_exito == 'benefício econômico':
    valor_honorario_exito = document.add_paragraph(f'c) Honorários de Êxito: {exito_percentual_formatado}% ({num_extenso_percentual(exito_percentual_formatado)}) do benefício econômico¹ aferido ao final do processo.')
    # valor_honorario_exito.add_footnote('Fica compreendido como benefício econômico todo e qualquer valor que a INTERESSADA receber em razão da propositura da ação ou valor que deixar de pagar.') # add a footnote
    format_paragraph(valor_honorario_exito, 3, 0, 1.5748, 18,18,18)
else:
    valor_honorario_exito = document.add_paragraph(f'c) Honorários de Êxito: {exito_percentual_formatado}% ({num_extenso_percentual(exito_percentual_formatado)}) {exito_outro_texto}.')
    # valor_honorario_exito.add_footnote('Em caso de acordo parcial, fica estipulado que o êxito poderá ser compatível com a redução que vier a ser atingida.') # add a footnote
    format_paragraph(valor_honorario_exito, 3, 0, 1.5748, 18,18,18)

#paragrafo III-IV
paragraph_three_four = document.add_paragraph('Não estão incluídos na proposta ora apresentada eventuais custos com a contratação de advogados correspondentes fora de Brasília, bem como as despesas a serem incorridas em virtude da execução dos serviços, tais como, cópias reprográficas, custas judiciais, honorários periciais, emolumentos com autenticação de cópias e reconhecimento de firmas, obtenção de certidões, motoboys e deslocamentos à razão de R$ 1,00/km, entre outras despesas, as quais serão pagas diretamente por V.Sa. ou reembolsadas mediante a apresentação dos respectivos comprovantes.')
format_paragraph(paragraph_three_four, 3, 1.5748, 0, 18,18,18)

#paragrafo III-IV.I
paragraph_three_four_one = document.add_paragraph("Eventuais despesas relativas a custas judiciais e extrajudiciais, como cópias, tributos, honorários periciais, bem como despesas com o eventual deslocamento e hospedagem de pessoal da Roque Khouri & Pinheiro Advogados Associados para fora de Brasília em razão da prestação de serviços serão de responsabilidade dos Interessados. Qualquer outro serviço ou indagação, incluindo também contatos informais por aplicativo de mensagem, também serão devidamente remunerados de acordo com as horas efetivamente trabalhadas.")
format_paragraph(paragraph_three_four_one, 3, 1.5748,0, 18,18,18)

#paragrafo III-IV.II
if valor_teto_exito > 0.0:
    paragraph_three_four_two = document.add_paragraph(f"Todos os valores aqui previstos serão devidamente atualizados anualmente pelo INPC ou índice que vier a substituí-lo. Todos os valores aqui previstos são devidos mesmo em caso de acordo. O valor do êxito fica limitado ao valor de R${valor_teto_exito_formatado}, devidamente atualizado.")
    format_paragraph(paragraph_three_four_two, 3, 1.5748,0, 18,18,18)
else:
    paragraph_three_four_two = document.add_paragraph("Todos os valores aqui previstos serão devidamente atualizados anualmente pelo INPC ou índice que vier a substituí-lo. Todos os valores aqui previstos são devidos mesmo em caso de acordo.")
    format_paragraph(paragraph_three_four_two, 3, 1.5748,0, 18,18,18)


#paragrafo III-V
paragraph_three_five = document.add_paragraph('Havendo necessidade de propositura de nova ação judicial que não aquela prevista no item I, deverá ser apresentado novo valor de honorários.')
format_paragraph(paragraph_three_five, 3, 1.5748, 0,18,18,18)


#############################################################################
# IV - DA CONFIDENCIALIDADE
#Tituolo
title_iv = document.add_heading('IV - DA CONFIDENCIALIDADE', level=2)
format_title_justified(title_iv)
paragraph = document.add_paragraph()
format_paragraph(paragraph, 3, 1.5748, 0, 18,18,18)
paragraph.text = "O escritório e seus profissionais comprometem-se a: (i) tratar todas as informações que tiverem acesso por meio deste trabalho de forma confidencial durante o prazo de realização das atividades; e (ii) não utilizar qualquer informação confidencial para qualquer fim que não a realização dos trabalhos. Excetua-se do conceito de informação confidencial aquela que já for divulgada ou disponibilizada publicamente pelo interessado."

#paragrafo IV-I
paragraph = document.add_paragraph()
format_paragraph(paragraph, 3, 1.5748, 0,18,18,18) 
paragraph.text = "Atenciosamente,"


# Adicionar parágrafo centralizado
paragraph = document.add_paragraph()
paragraph.add_run('Roque Khouri & Pinheiro Advogados Associados \nPaulo R. Roque A. Khouri\nOAB/DF 10.671').bold = True
paragraph_format = paragraph.paragraph_format
paragraph_format.alignment = 1  # Centralizado
paragraph_format.space_before = Pt(64)

# Adicionar parágrafo para "De acordo:"
paragraph = document.add_paragraph()
paragraph.add_run("De acordo:________________").bold = True
paragraph_format = paragraph.paragraph_format
paragraph_format.space_before = Pt(40)


# Adicionar parágrafo para "Data:"
paragraph = document.add_paragraph()
paragraph.add_run("Data:_____________________").bold = True
paragraph_format = paragraph.paragraph_format
paragraph_format.space_before = Pt(32)
paragraph = document.add_paragraph()

####################################
with desenvolvimento:
    while True:
        if nome_cliente:
            break
        time.sleep(2)
    st.markdown(f"""
        <div style="text-align: right;">
            {paragraph_date.text}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(title.text)
    # st.write(p_de.text)
    st.write(f'**{paragraph_para.text}**')
    st.write(paragraph_ref.text)
    st.write('*texto padrao apresentação do escritorio*')
    st.write(title_one.text)
    
    while True:
        if input_contencioso_objeto:
            break
        time.sleep(2)

    if input_contencioso_objeto:
        st.markdown(f"""
        <div style="text-align: justify;">
        {paragraph_objeto.text}
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.markdown(f"""
        <div style="text-align: justify;">
        A atuação desse Jurídico compreenderá as seguintes atividades:
        </div>
        """, unsafe_allow_html=True)

    # Recuo para os itens
    
    for item in itens_atuacao:
        st.markdown(f"""
        <div style="text-align: justify;">
        {recuo}-  {item}
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.write(f'*Texto padrão sobre: disposição de equipe, alerta sobre risco jurídico e política de honorários*')
    st.write("")
    st.markdown(f"""
    <div style="text-align: justify;">
    {title_three.text}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align: justify;">
    {paragraph_three_one_one.text}
    </div>
    """, unsafe_allow_html=True)


    if prolabore_inicial > 0.0:
        st.markdown(f"""
        <div style="text-align: justify;">
        <p>{recuo}{valor_prolabore_inicial.text}</p>
        <p>{recuo}{valor_honorario_manutencao.text}</p>
        <p>{recuo}{valor_honorario_exito.text}</p>
        <p><i>Texto padrão sobre os eventuais custos com a contratação de advogads e despesas relativas a custas judiciais</i></p>
        <p>{paragraph_three_four_two.text}</p>
        <p>{paragraph_three_four_two.text}</p>
        <p><i>Texto padrão sobre a necessidade de novo valor de honorários se propositura de nova ação judicial.</i></p>        
        <p>{title_iv.text}</p>        
        <p><i>Texto padrão sobre confidencialidade.</i></p>                
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.write("")
    st.write("")

    # Salvar documento em arquivo temporário e permitir download
    with NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        document.save(tmp_file.name)
        st.download_button(
            label="Baixar Documento",
            data=open(tmp_file.name, 'rb').read(),
            file_name=f'proposta_contencioso_{nome_cliente}.docx',
            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    if st.button('Salvar dados'):
        novo_dado = {
            'nome_cliente': nome_cliente,
            'objeto_contencioso': input_contencioso_objeto,
            'instancia_superior': instancia_,
            'orgao': orgao_,
            'itens_atuacao': itens_atuacao,
            'pro_labore_inicial': prolabore_inicial_formatado,
            # 'pro_labore_inicial_desconto':prolabore_inicial_com_desconto_fomatado,
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
        
        df_inputs = df_inputs.append(novo_dado, ignore_index=True)
        # Salvar o DataFrame atualizado no CSV
        df_inputs.to_csv('df_inputs.csv', index=False)

        # Limpar caracteres especiais no nome do cliente
        # nome_cliente_formatado = re.sub(r'[^\w\s]', '_', nome_cliente)
        # document.save(f".\documentos_gerados\proposta_contencioso_{nome_cliente_formatado}.docx")
        # st.success('Dados salvos com sucesso!')
    
