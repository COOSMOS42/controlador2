
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from gspread_pandas import Spread, Client
from gspread_dataframe import set_with_dataframe

# Definir escopos para Google Sheets e Google Drive
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Carregar as credenciais de acesso do arquivo JSON
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes= scope)
# Autenticar com o Google Sheets (conectar as credencias)
client = Client(scope=scope, creds=creds)
spreadsheetname = "controlador"
spread = Spread(spreadsheetname, client = client)
#link com a planilha do google sheets
sheet = client.open(spreadsheetname).sheet1

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

#impedir que a lista que está sendo criada reset(manter os dados)
if 'jsoninput' not in st.session_state:
    st.session_state.jsoninput = None

# impedir o reset da planilha
if 'plan' not in st.session_state:
    st.session_state.plan = fr


# adiciona um entrega
def adicionar_entrega(Data, Destinatario, Documento, Observacao):
    entrega = {
        'data': Data,
        'destinatario': Destinatario,
        'documento': Documento,
        'observacao': Observacao
    }

    st.session_state.jsoninput = pd.concat([st.session_state.jsoninput, pd.DataFrame(entrega, index=[0])],
                                           ignore_index=True)

    return st.session_state.jsoninput

st.header('CONTROLE DE ENTREGAS')

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':

    if st.button('ADICIONAR ENTREGA'):
            st.session_state.page = 'entregas'

    if st.button('CONSULTAR ENTREGAS'):
            st.session_state.page = 'consulta'

    if st.button('REMOVER ENTREGAS'):
            st.session_state.page = 'remover'

elif st.session_state.page == 'entregas':
    st.subheader('Gerenciamento de Entregas')

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

        st.subheader('Observação')
        obs = st.text_input('Alguma observação?')

        st.subheader('Adicionar entrega')

        if data == '' and destinatario == '' and documento == '':
            st.warning('Preencha todos os dados!')

        st.subheader('Salvar entregas')

        # cria um datafreame para que os dados contidos na lista jsoninput sejam alocadas para a planilha d google sheets
        st.session_state.jsoninput = pd.DataFrame(st.session_state.jsoninput)


        if st.form_submit_button('Adicionar'):
            st.session_state.jsoninput = adicionar_entrega(
                dataformat, destinatario, documento, obs)

    st.subheader('Salvar entregas')

    # cria um datafreame para que os dados contidos na lista jsoninput sejam alocadas para a planilha d google sheets
    st.session_state.jsoninput = pd.DataFrame(st.session_state.jsoninput)

    if st.button('Enviar para Google Sheets'):
        set_with_dataframe(sheet,
                           st.session_state.jsoninput,
                           row=len(sheet.col_values(1)) + 1,
                           include_column_header=False)
        st.success('Dados enviados com sucesso!')

    if st.button('Voltar ao início'):
        st.session_state.page = 'home'

elif st.session_state.page == 'consulta':
    st.subheader('Gerenciamento de Entregas')

    # formulário para procurar documentos na planilha do google sheets
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

    if st.button('Voltar ao início'):
        st.session_state.page = 'home'

elif st.session_state.page == 'remover':
    st.subheader('Gerenciamento de Entregas')

    # formulário para remoção de linhas da planilha do google sheets
    with st.form('rmv', clear_on_submit=True, border=True):
        st.subheader('Remover entrega')
        ind = st.number_input('Qual entrega deseja remover?', 1, 9999, 1)
        ind2 = ind + 1

        if st.form_submit_button('Remover'):
            sheet.delete_rows(ind2)

    if st.button('Voltar ao início'):
        st.session_state.page = 'home'
