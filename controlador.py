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

#lista das entrega feitas atravez do formulario, as entregas vão se acumulando nessa lista até o resete de site
if 'jsoninput' not in st.session_state:
    st.session_state.jsoninput = None


#adiciona um entrega a lista acima
# dia 07/11 foi alterado de Destinatário para Status pois não faz sentido manter como destinario se com status eu tenho mais informações
def adicionar_entrega(Data, Status, Documento, Observações, link):
    entrega = {
        'data': Data,
        'status': Status,
        'documento': Documento,
        'observações' : Observações,
        'link': link
    }

    st.session_state.jsoninput = pd.concat(
        [st.session_state.jsoninput,
         pd.DataFrame(entrega, index=[0])],
        ignore_index=True)

    return st.session_state.jsoninput


# Carregando as entregas ao iniciar a aplicação
st.header('Carregar entregas')

with st.sidebar:
    st.subheader('Como Preencher os dados')
    st.write('1º: Escolha a data de envio.')
    st.write('2º: Defina o Status.')
    st.write('3º: Defina um documento.')
    st.write('-Coloque primeiro o número da parcela em romanos por exemplo:')
    st.write('-Parecela cinco: V')
    st.write('-Em segundo coloque o nome do documento:')
    st.write('-Virgílio Távora I')
    st.write('-Texto final: V Virgílio Távora I')
    st.write('4º: Se não houver observação, deixar em branco')



    
st.subheader('Status')
status = st.selectbox('Escolha o Status', ('Entrega SS', 'Envio à prefeitura', 'Recebimento Revisão',
                                                 'Assinado pela SS', 'Reenvio à Prefeitura','Concluído', 'Encaminhado para Ajustes', 'Outro') )

status2 = None
if status == 'Outro':
    status2 = st.text_input('Qual o status?')
else:
    status2 = status
    
# formulário para preenchimento dos dados que serão inputados na lista cache
with st.form('Preencha os dados', clear_on_submit=True, border=True):
    st.subheader('Data')
    data = st.date_input('Data de envio',
                         datetime.now().date(),
                         format='DD/MM/YYYY')
    a = str(data)
    dataformat = f'{a[-2:]}/{a[5:7]}/{a[:4]}'

    st.subheader('Documento')
    parcela = st.selectbox('Escolha a Parcela', ('I', 'II', 'III',
                                                 'IV', 'V','VI', 'VII', 'VIII', 'IX', 'X', 'XI',
                                                 'XII') )
    documento = st.selectbox('Qual o documento referido?', ('Virgílio Távora I', 'Virgílio Távora II', 'Virgílio Távora III', 'Demócriot Dummar I', 'Demócriot Dummar II', 'Demócriot Dummar III', 'Blanchard Girão', 'Bonaparte Viana') )
    pardoc = parcela + " " + documento

    st.subheader('Observação')
    obs = st.text_input('Alguma observação?')

    st.subheader('Link do Documento')
    lnk = st.text_input('Adicione aqui o link do documento')

    st.subheader('Adicionar Status')

    if data == '' and destinatario == '' and documento == '':
        st.warning('Preencha todos os dados!')

    if st.form_submit_button('Adicionar'):
        st.session_state.jsoninput = adicionar_entrega(
            dataformat, status2, pardoc, obs, lnk)

st.subheader('Salvar entregas')

#cria um datafreame para que os dados contidos na lista jsoninput sejam alocadas para a planilha d google sheets
st.session_state.jsoninput = pd.DataFrame(st.session_state.jsoninput)

if st.button('Enviar para Google Sheets'):
    set_with_dataframe(sheet,
                       st.session_state.jsoninput,
                       row=len(sheet.col_values(1)) + 1,
                       include_column_header=False)
    st.success('Dados enviados com sucesso!')
