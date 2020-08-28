import streamlit as st
import pandas as pd
import altair as alt
import datetime
import urllib
import base64
#import openpyxl
import xlsxwriter
from io import BytesIO
from flask import send_file

st.title("Export de tabela")

@st.cache
def get_UN_data():
    AWS_BUCKET_URL = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")

try:
    df = get_UN_data()
except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
    #return

st.markdown(
"""
Selecione as colunas e linhas
""")

df = df.T.reset_index()
df = pd.melt(df, id_vars=["index"]).rename(
    columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
)

selected_columns = st.multiselect(
    "Escolhe colunas", list(df.columns), ["year"]
)
# if not selected_columns:
#     st.error("Please select at least one column.")
#     #return

selected_rows = st.multiselect(
    "Escolhe linhas", list(df.columns), ["Region"]
)
# if not selected_rows:
#     st.error("Please select at least one row.")
#     #return

df = df#.loc[countries]
#df /= 1000000.0
#df = df.T.reset_index()
df = df.pivot(
    index=selected_rows,
    columns=selected_columns,
    values="Gross Agricultural Product ($B)"
)
#if st.button('Exportar Excel'):
    #df.to_excel(f'Export_Orbita_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx')
    
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
    href = f'<a href="data:file/csv;base64,{b64}" download="Export_Orbita.csv">Download CSV file</a>'
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

st.markdown(get_table_download_link_csv(df), unsafe_allow_html=True)
#st.markdown(get_table_download_link_xlsx(df), unsafe_allow_html=True)

st.write("### Dados", df.sort_index())

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
