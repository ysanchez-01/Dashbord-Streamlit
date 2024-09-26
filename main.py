import pandas as pd
import streamlit as st
import plotly.express as px
import openai

st.markdown('<h1 style="color:navy;">Dashboard de Indicadores Financieros</h1>',unsafe_allow_html=True)
st.markdown(
    """Este proyecto es una aplicación web que permite a los usuarios evaluar ratios financieros por Industria, País y Tamaño."""
)

#2. Ingesta del Dataset Limpio en Streamlit
data = pd.read_csv(
    'https://raw.githubusercontent.com/ysanchez-01/Dashbord-Streamlit/refs/heads/main/Datos_proyecto_limpio.csv'
)

st.subheader("Acerca del conjunto de datos:")
#Mostramos los primeros datos de nuestro dataset
st.write(data.head())

#Mostramos las estadisticas básicas
st.write(data.describe().T)

st.subheader("Exploremos los datos:")

#3.Construcción del Dashboard Interactivo

# Filtros interactivos
industria_seleccionada = st.selectbox('Selecciona una Industria:',
                                      data['Industry'].unique())
pais_seleccionado = st.selectbox('Selecciona un País:',
                                 data['Country'].unique())
tamano_seleccionado = st.selectbox('Selecciona el Tamaño de la Empresa:',
                                   data['Company_Size'].unique())

# Filtrar los datos según la selección del usuario
data_filtrada = data[(data['Industry'] == industria_seleccionada)
                     & (data['Country'] == pais_seleccionado) &
                     (data['Company_Size'] == tamano_seleccionado)]

# Gráfico de Ratio de Liquidez
st.header('Ratio de Liquidez')
fig_liquidez = px.bar(data_filtrada,
                      x='Company_ID',
                      y='Current_Ratio',
                      title='Ratio de Liquidez por Empresa')
st.plotly_chart(fig_liquidez)

# Gráfico de Ratio Deuda a Patrimonio
st.header('Ratio Deuda a Patrimonio')
fig_deuda = px.line(data_filtrada,
                    x='Company_ID',
                    y='Debt_to_Equity_Ratio',
                    title='Ratio Deuda a Patrimonio por Empresa')
st.plotly_chart(fig_deuda)

# Gráfico de Cobertura de Gastos Financieros
st.header('Cobertura de Gastos Financieros')
fig_cobertura = px.pie(data_filtrada,
                       values='Interest_Coverage_Ratio',
                       names='Company_ID',
                       title='Cobertura de Gastos Financieros')
st.plotly_chart(fig_cobertura)

# Mostrar tabla de datos filtrados
st.header('Datos Filtrados')
st.dataframe(data_filtrada)

#4. Cálculo y Aplicación de Ratios Financieros
# Cálculos de los ratios financieros
data_filtrada['Ratio_Liquidez_Corriente'] = data_filtrada[
    'Current_Assets'] / data_filtrada['Current_Liabilities']
data_filtrada['Ratio_Deuda_a_Patrimonio'] = (
    data_filtrada['Short_Term_Debt'] +
    data_filtrada['Long_Term_Debt']) / data_filtrada['Equity']
data_filtrada['Cobertura_Gastos_Financieros'] = data_filtrada[
    'Total_Revenue'] / data_filtrada['Financial_Expenses']

# Mostrar los cálculos en un formato tabular
st.header('Ratios Financieros Calculados')
st.write('Estos son los ratios calculados para las empresas seleccionadas:')
st.dataframe(data_filtrada[[
    'Company_ID', 'Ratio_Liquidez_Corriente', 'Ratio_Deuda_a_Patrimonio',
    'Cobertura_Gastos_Financieros'
]])

#5.Integración de chatGPT
#pip install streamlit pandas seaborn matplotlib
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=openai_api_key)


# Función para obtener la respuesta de OpenAI
def obtener_respuesta(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Ajusta el modelo según lo que necesites
            messages=[{
                "role":
                "system",
                "content":
                """
                    Eres un financiero que trabaja para la aseguradora patito, eres experto en el área de solvencia,
                    entonces vas a responder todo desde la perspectiva de la aseguradora. Contesta siempre en español
                    en un máximo de 50 palabras.
                    """
            }, {
                "role": "user",
                "content": prompt
            }])
        output = response.choices[0].message['content']
        return output
    except Exception as e:
        st.error(f"Error al obtener respuesta de OpenAI: {e}")
        return None


# Pregunta interactiva a ChatGPT
st.header("Consulta con el asistente financiero")
user_prompt = st.text_input("Escribe tu consulta financiera aquí:")
if user_prompt:
    respuesta = obtener_respuesta(user_prompt)
    if respuesta:
        st.write(f"Respuesta: {respuesta}")
