import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import subprocess
import zipfile
import plotly.graph_objects as go


# command = "kaggle datasets download -d thedevastator/higher-education-predictors-of-student-retention"
# result = subprocess.run(command, shell=True, capture_output=True, text=True)
# with zipfile.ZipFile('higher-education-predictors-of-student-retention.zip', 'r') as zip_ref:
#     zip_ref.extractall()

df = pd.read_csv("dataset.csv")
# Titel van de applicatie
st.title("Slagingsstatus van studenten aan de hand van verschillende variabelen")

# Maak een sidebar met tabs
st.sidebar.title("Inhoud")
selected_tab = st.sidebar.radio("Kies een onderwerp", ["Geslacht", "Geslacht en leeftijd", "Avond/middag aanwezigheid", 
                                                       "Opleiding moeder/vader", "Cijfers per semester met wel/geen schulden"])


# Inhoud van Tab 1
if selected_tab == "Geslacht":
    st.header("Histogram met geslacht en slagingsstatus van studenten")
    st.write("Gebruik de checkbox om te filteren op geslacht (vrouw en/of man).")

    # Inladen dataset
    df = pd.read_csv('dataset.csv')

    # Vertaal de Target-categorieën naar Nederlands
    target_translation = {
        'Graduate': 'Afgestudeerd',
        'Dropout': 'Uitgevallen',
        'Enrolled': 'Ingeschreven'
    }

    df['Target'] = df['Target'].replace(target_translation)

    # Definieer de volgorde van de Target-categorieën
    target_order = ['Afgestudeerd', 'Uitgevallen', 'Ingeschreven']
    df['Target'] = pd.Categorical(df['Target'], categories=target_order, ordered=True)

    # Voeg checkboxes toe voor gender
    show_female = st.checkbox("Toon Vrouw", value=True)
    show_male = st.checkbox("Toon Man", value=True)

    # Filter de data op basis van de geselecteerde checkboxes
    if show_female and not show_male:
        filtered_df = df[df['Gender'] == 0]
    elif show_male and not show_female:
        filtered_df = df[df['Gender'] == 1]
    else:
        filtered_df = df  # Toon alles als beide opties geselecteerd zijn of geen selectie is gemaakt

    # Controleer of de gefilterde dataset niet leeg is
    if not filtered_df.empty:
        # Maak de Plotly countplot
        color_map = {
            "Afgestudeerd": "blue", 
            "Uitgevallen": "orange",
            "Ingeschreven": "green"
        }
        fig = px.histogram(
            filtered_df,
            x="Gender",
            color="Target",
            category_orders={"Target": target_order},
            barmode='group',
            labels={"Gender": "Geslacht", "Target": "Slagingsstatus", "count": "Aantal"},  # Labels hier aangepast
            color_discrete_map=color_map
        )

        # Pas de as-labels aan
        fig.update_layout(
            title = 'Slagingsstatus van studenten per geslacht',
            xaxis_title='Geslacht',
            yaxis_title='Aantal',
            xaxis=dict(tickmode='array', 
                        tickvals=[0, 1], 
                        ticktext=['Vrouw', 'Man'])
        )

        # Toon de Plotly-figuur in Streamlit
        st.plotly_chart(fig)
    else:
        st.write("Geen gegevens beschikbaar voor de geselecteerde filters.")

# Inhoud van Tab 2
elif selected_tab == "Geslacht en leeftijd":
    st.header("Histogram met geslacht, leeftijd en de slagingsstatus van studenten")
    st.markdown("Lijngrafieken van studiestatussen per Leeftijd: Uitgevallen, Ingeschreven en Afgestudeerd.")
    st.write("Gebruik de checkbox om te filteren op geslacht (vrouw en/of man).")
    st.write("Gebruik de slider om een bepaalde leeftijdscategorie te selecteren.")

    # Inladen dataset
    df = pd.read_csv('dataset.csv')

    # Voeg checkboxes toe voor gender
    show_female = st.checkbox("Toon Vrouw", value=True)
    show_male = st.checkbox("Toon Man", value=True)

    # Filter de data op basis van de geselecteerde checkboxes
    if show_female and not show_male:
        filtered_df = df[df['Gender'] == 0]
    elif show_male and not show_female:
        filtered_df = df[df['Gender'] == 1]
    else:
        filtered_df = df  # Toon alles als beide opties geselecteerd zijn of geen selectie is gemaakt
    
    # Slider voor leeftijdsfilter
    age_range = st.slider("Leeftijd range", 17, 50, (17, 50))
    
    # Filter de data verder op de geselecteerde leeftijdsrange
    filtered_df = filtered_df[(filtered_df['Age at enrollment'] >= age_range[0]) & (filtered_df['Age at enrollment'] <= age_range[1])]
    
    # Kruistabel plus percentage kolommen met de gefilterde dataset
    df_age = pd.crosstab(filtered_df['Age at enrollment'], filtered_df['Target'])
    df_age['Totaal'] = df_age['Dropout'] + df_age['Enrolled'] + df_age['Graduate']
    df_age['Dropout%'] = df_age['Dropout'] / df_age['Totaal']
    df_age['Enrolled%'] = df_age['Enrolled'] / df_age['Totaal']
    df_age['Graduate%'] = df_age['Graduate'] / df_age['Totaal']
    
    # Maak de dataframe klaar voor een plot
    df_age = df_age.reset_index()
    df_long = pd.melt(df_age, id_vars=['Age at enrollment'], value_vars=['Dropout%', 'Enrolled%', 'Graduate%'],
                      var_name='Column', value_name='Value')
    
    # Kleur de plot
    color_map = {
        'Dropout%': 'orange',
        'Enrolled%': 'green',
        'Graduate%': 'blue'
    }
    
    # Plot
    fig = px.line(df_long, x='Age at enrollment', y='Value', color='Column', color_discrete_map=color_map)
    
    # Update de legenda naar het Nederlands
    fig.for_each_trace(lambda t: t.update(name={
        'Dropout%': 'Uitgevallen%',
        'Enrolled%': 'Ingeschreven%',
        'Graduate%': 'Afgestudeerd%'
    }.get(t.name, t.name)))

    fig.update_xaxes(range=[age_range[0], age_range[1]])
    fig.update_layout(title='Percentage status van studenten per leeftijd',
                      xaxis_title='Leeftijd',
                      yaxis_title='Percentage',
                      legend_title_text='Slagingsstatus%')
    
    st.plotly_chart(fig)

# Inhoud van Tab 3
elif selected_tab == "Avond/middag aanwezigheid":
    st.header("Histogram met avond/middag aanwezigheid en slagingsstatus van studenten")
    st.write("Gebruik de checkbox om te filteren op aanwezigheid (avond en/of middag).")
    
    # Inladen dataset
    df = pd.read_csv('dataset.csv')
    
    # Vertaal de Target-categorieën naar Nederlands
    target_translation = {
        'Graduate': 'Afgestudeerd',
        'Dropout': 'Uitgevallen',
        'Enrolled': 'Ingeschreven'
    }

    df['Target'] = df['Target'].replace(target_translation)

    # Definieer de volgorde van de Target-categorieën
    target_order = ['Afgestudeerd', 'Uitgevallen', 'Ingeschreven']

    # Zorg ervoor dat de Target-kolom als categorisch wordt beschouwd en de volgorde vasthoudt
    df['Target'] = pd.Categorical(df['Target'], categories=target_order, ordered=True)

    # Voeg checkboxes toe voor gender
    show_avond = st.checkbox("Toon avondaanwezigheid", value=True)
    show_middag = st.checkbox("Toon middagaanwezigheid", value=True)

    # Filter de data op basis van de geselecteerde checkboxes
    if show_avond and not show_middag:
        filtered_df = df[df['Daytime/evening attendance'] == 0]
    elif show_middag and not show_avond:
        filtered_df = df[df['Daytime/evening attendance'] == 1]
    else:
        filtered_df = df  # Toon alles als beide opties geselecteerd zijn of geen selectie is gemaakt

    # Maak de plotly histogram
    # Controleer of de gefilterde dataset niet leeg is
    if not filtered_df.empty:

        # Maak de Plotly countplot
        color_map = {
            "Afgestudeerd": "blue", 
            "Uitgevallen": "orange",
            "Ingeschreven": "green"
        }
        fig = px.histogram(filtered_df, 
                        x="Daytime/evening attendance", 
                        color="Target", 
                        category_orders={"Target": target_order},
                        barmode='group',  # Zet de barmode op 'group' om ze naast elkaar te tonen
                        labels={"Daytime/evening attendance": "Avond/middag aanwezigheid", "Target": "Slagingsstatus", "count": "Aantal"},
                        color_discrete_map=color_map)
        
        # Pas de as-labels aan
        fig.update_layout(
                        title = 'Slagingsstatus van studenten aan de hand van aanwezigheid (middag of avond)',
                        xaxis_title='Avond/middag aanwezigheid', 
                        yaxis_title='Aantal',
                        xaxis=dict(tickmode='array', 
                                    tickvals=[0, 1], 
                                    ticktext=['Avond', 'Middag']))

        # Toon de Plotly-figuur in Streamlit
        st.plotly_chart(fig)

# Inhoud van Tab 4
elif selected_tab == "Opleiding moeder/vader":
    st.header("Histogram met opleiding moeder/vader en slagingsstatus van studenten.")
    st.markdown("Toelichting opleidingsniveau:")
    st.markdown('**Ongeschoold:** Kan niet/slecht lezen en schrijven  \n**Lager onderwijs**: Heeft de basisschool afgerond  \n**Hoger onderwijs**: Heeft de middelbare school afgerond  \n**Aanvullend onderwijs**: Heeft de middelbare school + extra course afgerond  \n**Opleiding**: Heeft een opleiding afgerond  \n**Onbekend**: Opleidingsniveau niet bekend')
    st.write("Gebruik de checkbox om te filteren op ouder (moeder en/of vader).")

    # Inladen dataset
    df = pd.read_csv('dataset.csv')
   
    # Vertaal de Target-categorieën naar Nederlands
    target_translation = {
        'Graduate': 'Afgestudeerd',
        'Dropout': 'Uitgevallen',
        'Enrolled': 'Ingeschreven'
    }

    df['Target'] = df['Target'].replace(target_translation)

    # Definieer de volgorde van de Target-categorieën
    target_order = ['Afgestudeerd', 'Uitgevallen', 'Ingeschreven']
    df['Target'] = pd.Categorical(df['Target'], categories=target_order, ordered=True)
    
    # Functie om de opleiding te bepalen
    def opleiding_ouders(x):
        if x in [25, 26]:
            return "Ongeschoold"
        elif x in [9, 18, 20, 21, 27, 28]:
            return "Lager Onderwijs"
        elif x in [1, 7, 8, 10, 12, 14, 19]:
            return 'Hoger Onderwijs'
        elif x in [11, 13, 15, 16, 17, 22, 29, 31, 32]:
            return 'Aanvullend Onderwijs'
        elif x in [2, 3, 4, 5, 6, 23, 30, 33, 34]:
            return 'Opleiding'
        else:
            return 'Onbekend'

    # Toepassen van de functie op beide kolommen
    df['Opleiding moeder'] = df["Mother's qualification"].map(opleiding_ouders)
    df['Opleiding vader'] = df["Father's qualification"].map(opleiding_ouders)

    # Maak een lange DataFrame met beide ouders
    df_combined = pd.DataFrame({
        'Ouder': ['Moeder'] * len(df) + ['Vader'] * len(df),
        'Opleiding': list(df['Opleiding moeder']) + list(df['Opleiding vader']),
        'Target': list(df['Target']) * 2  # Neem de 'Target' kolom voor beide ouders
    })

    # Voeg checkboxes toe voor gender
    show_moeder = st.checkbox("Toon moeder", value=True)
    show_vader = st.checkbox("Toon vader", value=True)

    # Filter de data op basis van de geselecteerde checkboxes
    if show_moeder and not show_vader:
        df_combined = df_combined[df_combined['Ouder'] == 'Moeder']
    elif show_vader and not show_moeder:
        df_combined = df_combined[df_combined['Ouder'] == 'Vader']
    else:
        df_combined = df_combined  # Toon alles als beide opties geselecteerd zijn of geen selectie is gemaakt

    # Selectbox om een opleidingsniveau te kiezen
    option_selected = st.selectbox("Kies opleidingsniveau", df_combined['Opleiding'].unique())

    # Filteren van de DataFrame op basis van de geselecteerde opleidingsniveau
    df_filtered = df_combined[df_combined['Opleiding'] == option_selected]
    
    # Controleer of de gefilterde DataFrame gegevens bevat
    if df_filtered.empty:
        st.write("Geen gegevens beschikbaar voor de geselecteerde filter.")
    else:
        # Kleuren kiezen
        color_map = {
            "Afgestudeerd": "blue", 
            "Uitgevallen": "orange",
            "Ingeschreven": "green"
        }
        
        # Creëer een histogram voor de geselecteerde opleidingsniveau, gescheiden per ouder
        fig = px.histogram(df_filtered, x='Ouder', color='Target', 
                        title=f'Opleidingsniveau ouders: {option_selected}',
                        labels = {"Ouder": "Ouder", "Target": "Slagingsstatus", "count": "Aantal"},
                        color_discrete_map=color_map,
                        barmode='stack')

        # Aanpassen van de lay-out van de grafiek
        fig.update_layout(
                        title = 'Slagingsstatus van studenten aan de hand van opleiding ouders.',
                        yaxis_title='Aantal',)

        # Plot de grafiek in Streamlit
        st.plotly_chart(fig)
    

# Inhoud van Tab 5
elif selected_tab == "Cijfers per semester met wel/geen schulden":
    st.header("Boxplot met cijfers per semester en wel/geen schulden")
    st.write("Gebruik de checkbox om te filteren op geslacht (vrouw en/of man).")
    
    # Inladen dataset
    df = pd.read_csv('dataset.csv')

    # Maakt een checkbox
    gender_option = st.checkbox("Vrouw", value=False)
    gender_option2 = st.checkbox("Man", value=False)
   
    # Verwijderd alle cijfers onder de tien
    df2 = df[['Curricular units 1st sem (grade)','Curricular units 2nd sem (grade)',  'Debtor', 'Gender']]
    df2 = df2[(df2['Curricular units 1st sem (grade)'] >= 10) & (df2['Curricular units 2nd sem (grade)'] >= 10)]
    df2 = df2.replace({'Debtor':{0: 'Geen schuld', 1: 'Schulden'}})
 
    if gender_option and gender_option2:
        df3 = df2
    elif gender_option:
        df3 = df2[df2['Gender'] == 0]
    elif gender_option2:
        df3 = df2[df2['Gender'] == 1]
    else:
        df3 = df2[df2['Gender'] == 3]
 
    # Maakt boxplot eerste semester
    fig = go.Figure()
    fig.add_trace(go.Box(x=df3['Curricular units 1st sem (grade)'],
                     y=df3['Debtor'],
                     name = 'Cijfer semester één',
                     marker_color='orange'))
 
    #    Maakt boxplot tweede semester
    fig.add_trace(go.Box(x=df3['Curricular units 2nd sem (grade)'],
                     y=df3['Debtor'],
                     name = 'Cijfer semester twee',
                     marker_color='green'))
    # Voegt titel toe
    fig.update_layout(
            title = 'Cijfers per semester voor mensen met en zonder schuld',
            xaxis=dict(title='Cijfers', zeroline=False),
            boxmode='group')
    
    #Laat boxpplot horizontaal zien
    fig.update_traces(orientation='h')

    # Plot de grafiek in Streamlit
    st.plotly_chart(fig)
