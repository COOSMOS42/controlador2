import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from gspread_pandas import Spread, Client
from gspread_dataframe import set_with_dataframe


# Definir escopos para Google Sheets e Google Drive
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Carregar as credenciais de acesso do arquivo JSON
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes= scope)
# Autenticar com o Google Sheets (conectar as credencias)
client = Client(scope = scope, creds = creds)
spreadsheetname = "controlador"
spread = Spread(spreadsheetname, client = client)
#link com a planilha do google sheets
sheet = client.open("controlador").sheet1

val = sheet.get_all_values()
# fr é a variavel da planilha do google sheets
fr = pd.DataFrame(val)
#separa a primeira linha da planilha google sheets
cab = fr.iloc[0]
#fazendo com que a planilha seja lida a partir da primeira linha
fr = fr[1:]
#seta as colunas
fr.columns = cab
st.set_page_config(page_title='Sistema de Cadastramento de Entregas',
                   layout='wide')

#lista das entrega feitas atravez do formulario, as entregas vão se acumulando nessa lista até o resete de site
if 'jsoninput' not in st.session_state:
    st.session_state.jsoninput = None


#adiciona um entrega a lista acima
def adicionar_entrega(Data, Destinatario, Documento):
    entrega = {
        'data': Data,
        'destinatario': Destinatario,
        'documento': Documento
    }

    st.session_state.jsoninput = pd.concat(
        [st.session_state.jsoninput,
         pd.DataFrame(entrega, index=[0])],
        ignore_index=True)

    return st.session_state.jsoninput


# Carregando as entregas ao iniciar a aplicação
st.header('Carregar entregas')
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    # formulário para preenchimento dos dados que serão inputados na lista cache
    with st.form('Preencha os dados', clear_on_submit=True, border=True):
        st.subheader('Data')
        data = st.date_input('Data de envio',
                             datetime.now().date(),
                             format='DD/MM/YYYY')
        a = str(data)
        dataformat = f'{a[-2:]}/{a[5:7]}/{a[:4]}'

        st.subheader('Destinatário')
        destinatario = st.text_input('Qual o destinatário?')

        st.subheader('Documento')
        documento = st.text_input('Qual documento foi enviado?')

        st.subheader('Adicionar entrega')

        if data == '' and destinatario == '' and documento == '':
            st.warning('Preencha todos os dados!')

        if st.form_submit_button('Adicionar'):
            st.session_state.jsoninput = adicionar_entrega(
                dataformat, destinatario, documento)
with col2:
    #formulário para remoção de linhas da planilha do google sheets
    with st.form('rmv', clear_on_submit=True, border=True):
        st.subheader('Remover entrega')
        ind = st.number_input('Qual entrega deseja remover?', 1, 9999, 1)
        ind2 = ind + 1

        if st.form_submit_button('Remover'):
            sheet.delete_rows(ind2)
#formulário para procurar documentos na planilha do google sheets
    with st.form('proc', clear_on_submit=True, border=True):
        st.subheader('Procurar entregas')
        crit = st.selectbox('Selecione um critério:',
                            ['data', 'destinatario', 'documento'])
        dat = st.text_input('Escreva o valor correspondente')

        # fr é a varaivel que contem a planilha do google sheets
        if st.form_submit_button('Procurar'):

            if crit == 'data':
                df = fr[fr['data'] == dat]
            if crit == 'destinatario':
                df = fr[fr['destinatario'] == dat]
            if crit == 'documento':
                df = fr[fr['documento'] == dat]

            st.dataframe(df, use_container_width=True)

    st.subheader('Salvar entregas')

    #cria um datafreame para que os dados contidos na lista jsoninput sejam alocadas para a planilha d google sheets
    st.session_state.jsoninput = pd.DataFrame(st.session_state.jsoninput)

    if st.button('Enviar para Google Sheets'):
        set_with_dataframe(sheet,
                           st.session_state.jsoninput,
                           row=len(sheet.col_values(1)) + 1,
                           include_column_header=False)
        st.success('Dados enviados com sucesso!')

with col3:
    with st.form('me', clear_on_submit=True, border=True):
        st.subheader('Mostrar entregas')
        if st.form_submit_button('Mostrar'):
            st.dataframe(fr, use_container_width=True, height=800)
