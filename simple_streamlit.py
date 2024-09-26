import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

df = pd.read_csv('dataset.csv')

st.markdown('Lijngrafieken van studiestatussen per Leeftijd: Uitgevallen, Ingeschreven en Afgestudeerd')

gender_option = st.checkbox("Filter bij gender")

df['Gender'] = df['Gender'].map({1: 'Man', 0: 'Vrouw'})

if gender_option:
    gender_selected = st.multiselect("Select Gender", df['Gender'].unique(), default=df['Gender'].unique())
    df = df[df['Gender'].isin(gender_selected)]
 
#slider
age_range = st.slider("Leeftijd range", 17, 50, (17, 50))
 
#kruistabel plus percentage kolommen
df_age = pd.crosstab(df['Age at enrollment'], df['Target'])
df_age['Totaal'] = df_age['Dropout'] + df_age['Enrolled'] + df_age['Graduate']
df_age['Dropout%'] = df_age['Dropout']/df_age['Totaal']
df_age['Enrolled%'] = df_age['Enrolled']/df_age['Totaal']
df_age['Graduate%'] = df_age['Graduate']/df_age['Totaal']
 
#df klaar maken voor een plot
df_age = df_age.reset_index()
df_long = pd.melt(df_age, id_vars=['Age at enrollment'], value_vars=df_age.columns[5:8],
                  var_name='Column', value_name='Value')
 
#kleur de plot
color_map = {
    df_age.columns[5]: 'orange',
    df_age.columns[6]: 'green',
    df_age.columns[7]: 'blue'
}
 
#plot
fig = px.line(df_long, x='Age at enrollment', y='Value', color='Column', color_discrete_map=color_map)
 
fig.update_xaxes(range=[age_range[0], age_range[1]])
fig.update_layout(title='Percentage status van studenten per leeftijd',
                   xaxis_title='Leeftijd',
                   yaxis_title='Percentage')
st.plotly_chart(fig)