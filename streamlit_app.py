import streamlit as st
import pandas as pd
import altair as alt
import datetime
import urllib
import base64
import requests
from io import StringIO, BytesIO
import base64
import xlsxwriter
from itertools import compress

#import openpyxl
#from io import BytesIO
#from flask import send_file

st.title("Crie sua tabela")
#st.markdown('v0.4.0')
st.markdown(
"""### Tabela fonte
#### Tesouro Transparente - Transferências Constitucionais para Municípios
Parcela das receitas federais arrecadadas pela União é repassada aos Municípios. O rateio da receita proveniente da arrecadação de impostos entre os entes federados representa um mecanismo fundamental para amenizar as desigualdades regionais, na busca incessante de promover o equilíbrio sócio-econômico entre Estados.

Cabe ao Tesouro Nacional, em cumprimento aos dispositivos constitucionais, efetuar as transferências desses recursos aos entes federados, nos prazos legalmente estabelecidos.

Dentre as principais transferências da União para os Municípios, previstas na Constituição, destacam-se: o Fundo de Participação dos Estados e do Distrito Federal (FPE); o Fundo de Participação dos Municípios (FPM); o Fundo de Compensação pela Exportação de Produtos Industrializados - FPEX; o Fundo de Manutenção e Desenvolvimento da Educação Básica e de Valorização dos Profissionais da Educação - Fundeb; e o Imposto sobre a Propriedade Territorial Rural - ITR.

Dados disponíveis nesta aplicação são referentes ao mês de março em anos 2017, 2018, 2019 e 2020.""")

#@st.cache
def get_UN_data():
    AWS_BUCKET_URL = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")

def get_SIDRA_POC_table01_google_drive():
    #return pd.read_csv('https://drive.google.com/file/d/1poUgFZBahCC7QmQX_hgVuZ7D-emxLnQD/view', error_bad_lines=False)
    orig_url='https://drive.google.com/file/d/1poUgFZBahCC7QmQX_hgVuZ7D-emxLnQD/view'

    file_id = orig_url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?export=download&id=' + file_id
    url = requests.get(dwn_url).text
    csv_raw = StringIO(url)
    return pd.read_csv(csv_raw, error_bad_lines=False)

def get_SIDRA_POC_table02():
    return pd.read_csv('data_mock/silver_tesourotransparente_transferencias-constitucionais-para-municipios_Transferencia_Mensal_Municipios_mes03.csv', sep=';')

try:
    #df = get_UN_data()
    df = get_SIDRA_POC_table02().drop('mes',1)
    df['todos os decendios'] = df['1o decendio']+df['2o decendio']+df['3o decendio']
except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
    #return

# st.markdown(
# """
# Selecione as colunas e linhas
# """)

#df = df.T.reset_index()
#df = pd.melt(df, id_vars=["index"]).rename(
#    columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
#)


available_rows_columns = ['ano', 'uf', 'municipio', 'transferencia', 'item transferencia']
available_variables = ['1o decendio', '2o decendio', '3o decendio', 'todos os decendios']
#available_rows_columns = df.columns

st.markdown(
"""### Colunas e linhas
Selecione quais dimensões serão utilizadas como colunas e quais como linhas""")
#selected_columns = []
#selected_rows = []

selected_columns = st.multiselect(
    "Colunas", available_rows_columns#list(df.columns)#, [df.columns[0]]
)
# if not selected_columns:
#     st.error("Please select at least one column.")
#     #return

selected_rows = st.multiselect(
    "Linhas", available_rows_columns#list(df.columns)#, [df.columns[1]]
)
# if not selected_rows:
#     st.error("Please select at least one row.")
#     #return

exists_intersection = False
empty_complement = True

complement = set(available_rows_columns)-set(selected_columns+selected_rows)
if len(complement) > 0:
    st.markdown("##### Dimensões obrigatórias para escolher como coluna ou linha:\n"+('  \n'.join(complement)))
    empty_complement = False

intersection = set(selected_columns).intersection(set(selected_rows))
if len(intersection) > 0:
    st.markdown(f"""##### Dimensões não podem ser escolhidos como coluna e linha ao mesmo tempo
{', '.join(intersection)}
""")
    exists_intersection = True

#is_not_value = [True]*len(df.columns)
#is_value = [False]*len(df.columns)
is_value = [False]*len(available_variables)
st.markdown("### Variável")
#if True not in is_value:
for i in range(len(available_variables)):
    #c = df.columns[i]
    #is_not_value[i] = not st.checkbox(c, False)
    #is_value[i] = not is_not_value[i]
    is_value[i] = st.checkbox(available_variables[i], True)

#available_rows_columns = list(compress(available_rows_columns, is_not_value))
values = list(compress(available_variables, is_value))
variables_selected = True
if len(values) == 0:
    st.markdown('##### Escolhe ao menos 1 variável.')
    st.text('')
    variables_selected = False


#value = st.selectbox('Valor usado', values)
#value = '1o decendio'

st.markdown("### Ano")
anos = df['ano'].unique()#.sort()
use_year = [False]*len(anos)
for i in range(len(anos)):
    use_year[i] = st.checkbox(str(anos[i]), True)
#st.text(use_year)

anos = list(compress(anos, use_year))
years_selected = True
if len(anos) == 0:
    st.markdown('##### Escolhe ao menos 1 ano.')
    st.text('')
    years_selected = False

df = df[df['ano'].isin(anos)]
    
st.markdown("### UF")
ufs = df['uf'].unique()#.sort()
use_uf = [False]*len(ufs)
select_all_ufs = st.checkbox('Selecionar todos', True)
for i in range(len(ufs)):
    use_uf[i] = st.checkbox(str(ufs[i]), select_all_ufs)
#st.text(use_uf)

ufs = list(compress(ufs, use_uf))
ufs_selected = True
if len(ufs) == 0:
    st.markdown('##### Escolhe ao menos 1 UF.')
    st.text('')
    ufs_selected = False

df = df[df['uf'].isin(ufs)]

if not exists_intersection and empty_complement and variables_selected and years_selected and ufs_selected:
    #df = df[selected_columns+selected_rows+values]
    #df /= 1000000.0
    #df = df.T.reset_index()
    #if not empty_complement:
    df_pivot = df[selected_columns+selected_rows+values].pivot(
        index=selected_rows if len(selected_rows)>0 else None,
        columns=selected_columns,
        values=values
    )
    # else:
    #     df_pivot = df.head(10000) \
    #         .reset_index() \
    #         .pivot(index=selected_rows+['index'], columns=selected_columns, values=values) \
    #         .reset_index(level='index', drop=True)
    #     #if multiindex: #Can only reorder levels on a hierarchical axis.
    #     #    df_pivot = df_pivot.reorder_levels([*selected_columns,0], 1)


    #if st.button('Exportar Excel'):
        # df.to_excel(f'Export_Orbita_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx')
        
        # output = BytesIO()
        # writer = pd.ExcelWriter(output, engine='xlsxwriter')
        # df.to_excel(writer, sheet_name='Sheet1')
        # writer.save()
        # output.seek(0)
        # send_file(output, attachment_filename='Export_Orbita.xlsx', as_attachment=True)
    #if st.button('Exportar CSV'):
    #    df.to_csv(f'Export_Orbita_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv')

    def get_table_download_link_csv(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv()
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" target="_blank" download="Export_Orbita.csv">Baixar CSV</a>'
        return href

    def get_table_download_link_xlsx(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """

        writer = pd.ExcelWriter('.', engine='xlsxwriter')
        df.to_excel('Export_Orbita.xlsx', engine='xlsxwriter')
        # b64 = base64.b64encode(xlsx_file.encode()).decode()  # some strings <-> bytes conversions necessary here
        #href = f'<a href="data:file/xlsx;base64,{b64}" download="Export_Orbita.xlsx">Download Excel file</a>'

        href = '<a href="Export_Orbita.xlsx" target="_blank" download="Export_Orbita.xlsx">Download Excel file</a>'
        return href

    def send_excel2(df):
        strIO = BytesIO()
        excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
        df.to_excel(excel_writer, sheet_name="sheet1")
        excel_writer.save()
        excel_data = strIO.getvalue()
        strIO.seek(0)

        return send_file(strIO,
                        attachment_filename='Export_Orbita.xlsx',
                        as_attachment=True)

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    def get_table_download_link_xlsx2(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        val = to_excel(df)
        b64 = base64.b64encode(val)  # val looks like b'...'
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Export_Orbita.xlsx">Baixar XLSX</a>' # decode b'abc' => abc


    st.markdown('### Tabela customizada')
    if st.button('Gerar CSV'):
        st.markdown(get_table_download_link_csv(df_pivot), unsafe_allow_html=True)
    if st.button('Gerar XLSX'):
        within_limits = True
        if df_pivot.shape[0] > 1048576:
            within_limits = False
            st.markdown('##### O número de linhas da tabela a ser exportada excede o limite suportado por Excel.')
            st.text('')
        if df_pivot.shape[1] > 16384:
            within_limits = False
            st.markdown('##### O número de colunas da tabela a ser exportada excede o limite suportado por Excel.')
            st.text('')
        
        if within_limits:
            st.markdown(get_table_download_link_xlsx2(df_pivot), unsafe_allow_html=True)

    #st.write("### Dados", df.head(20))
    if st.button('Exibir tabela'):
        st.write(df_pivot)
    #st.write(f"""### Tabela customizada
    #""", df_pivot)#.head(50))
#Layout: 1 tabela [{max(1, len(selected_rows))} x {max(1, len(selected_columns))}] - {max(1, len(selected_rows)) * max(1, len(selected_columns))} valores

    # df = df.T.reset_index()
    # df = pd.melt(df, id_vars=["index"]).rename(
    #     columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
    # )
    # chart = (
    #     alt.Chart(df)
    #     .mark_area(opacity=0.3)
    #     .encode(
    #         x="year:T",
    #         y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
    #         color="Region:N",
    #     )
    # )
    # st.altair_chart(chart, use_container_width=True)
else:
    st.markdown("""### Pendências
Para gerar a tabela, favor resolver as pendências em sua configuração, observando as mensagens embaixo de cada seção.""")