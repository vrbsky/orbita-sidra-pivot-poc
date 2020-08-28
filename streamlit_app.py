import streamlit as st
import pandas as pd
import altair as alt
import datetime

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
    "Escolhe colunas", list(df.columns)#, ["year"]
)
# if not selected_columns:
#     st.error("Please select at least one column.")
#     #return

selected_rows = st.multiselect(
    "Escolhe linhas", list(df.columns)#, ["Region"]
)
# if not selected_rows:
#     st.error("Please select at least one row.")
#     #return

data = df#.loc[countries]
#data /= 1000000.0
#data = data.T.reset_index()
data = data.pivot(
    index=selected_rows,
    columns=selected_columns,
    values="Gross Agricultural Product ($B)"
)
if st.button('Exportar Excel'):
    df.to_excel(f'Export_Orbita_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx')
if st.button('Exportar CSV'):
    df.to_csv(f'Export_Orbita_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv')
st.write("### Dados", data.sort_index())


# data = data.T.reset_index()
# data = pd.melt(data, id_vars=["index"]).rename(
#     columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
# )
# chart = (
#     alt.Chart(data)
#     .mark_area(opacity=0.3)
#     .encode(
#         x="year:T",
#         y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
#         color="Region:N",
#     )
# )
# st.altair_chart(chart, use_container_width=True)
