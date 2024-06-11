import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import json
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

st.set_page_config(layout="wide")


# Function to load and preprocess data
@st.cache_data
def load_data(csv_path, geojson_path):
    df = pd.read_csv(csv_path)
    df['lat'] = df['lat'].str.replace(',', '.').astype(float)
    df['long'] = df['long'].str.replace(',', '.').astype(float)
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    return df, geojson_data


# Function to create folium map
def create_folium_map(df, geojson_data, center, zoom_start=12):
    mymap = folium.Map(location=center, zoom_start=zoom_start)
    folium.GeoJson(geojson_data, name='Pistes Cyclables', show=False).add_to(mymap)
    folium.TileLayer('openstreetmap').add_to(mymap)
    marker_cluster = MarkerCluster().add_to(mymap)
    for accident in df.itertuples(index=False):
        popup_html = f'''
        <div style="color: black;">
            <strong>Date:</strong> {accident.date}<br>
            <strong>Gravité:</strong> {accident.gravite}<br>
            <strong>Adresse:</strong> {accident.adresse}<br>
            <strong>Lumière:</strong> {accident.éclairage}<br>
            <strong>Météo:</strong> {accident.meteo}<br>
            <strong>Collision:</strong> {accident.collision}<br>
            <strong>Situation:</strong> {accident.situation}<br>
            <strong>Trajet:</strong> {accident.trajet}<br>
            <strong>Sécurité 1:</strong> {accident.secu1}<br>
            <strong>Sécurité 2:</strong> {accident.secu2}<br>
            <strong>Sécurité 3:</strong> {accident.secu3}
        </div>
        '''
        folium.Marker(
            location=[accident.lat, accident.long],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='red')
        ).add_to(marker_cluster)
    folium.LayerControl().add_to(mymap)
    return mymap


# Function to create pie chart
def create_pie_chart(data, column, title):
    data_counts = data[column].value_counts().reset_index()
    data_counts.columns = [column, 'count']
    fig = px.pie(
        data_counts,
        values='count',
        names=column,
        title=title,
        template='seaborn',
    )
    fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig, use_container_width=True)


def create_bar_chart(data, column, title):
    data_counts = data[column].value_counts().reset_index()
    data_counts.columns = [column, 'count']
    fig = px.bar(
        data_counts,
        x=column,
        y='count',
        color=column,
        text='count',
        labels={column: column, 'count': 'count', 'text': 'count'},
        template='seaborn',
        text_auto=True,
        title=title
    )
    fig.update_layout(title={'x': 0.5, 'xanchor': 'center'}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def create_line_chart(data, column, title):
    data_counts = data[column].value_counts().reset_index()
    data_counts.columns = [column, 'count']
    data_counts = data_counts.sort_values(by=column)
    fig = px.line(
        data_counts,
        x=column,
        y='count',
        title=title,
        labels={column: column, 'count': 'count'},
        text='count',
        template='seaborn'
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(title={'x': 0.5, 'xanchor': 'center'},
                      xaxis=dict(tickmode='linear'),
                      yaxis=dict(range=[0, data_counts['count'].max() + 1]))
    st.plotly_chart(fig, use_container_width=True)


# Load data
csv_path = './accidents-velo-31-clean.csv'
geojson_path = './filtered_france_tls_20240601.geojson'
df, geojson_data = load_data(csv_path, geojson_path)
df['date_heure'] = pd.to_datetime(
    df['annee'].astype(str) + '-' +
    df['mois'].astype(str) + '-' +
    df['jour'].astype(str) + ' ' +
    df['hrmn'].astype(str)
)

# Create map centered on Toulouse, France
map_center = [43.6045, 1.444]
mymap = create_folium_map(df, geojson_data, map_center)

# Streamlit title and map display
st.markdown("""
    <div style="text-align: center;">
        <h1>Toulouse : carte des accidents de vélo</h1>
        <p>Cette carte montre les accidents de vélo à Toulouse ainsi que les pistes cyclables.</p>
    </div>
    """, unsafe_allow_html=True)

# Centering the map
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    folium_static(mymap, width=1000, height=700)

# Tabs for additional visualizations
tab5, tab6, tab7, tab8, tab9 = st.tabs(['Année', 'Mois', 'Jour/mois', 'Jour/semaine', 'Heure'])

with tab5:
    df['year'] = df['date_heure'].dt.year
    create_line_chart(df, 'year', 'Nombre d\'accidents par année')

with tab6:
    df['month'] = df['date_heure'].dt.month
    create_line_chart(df, 'month', 'Nombre d\'accidents par mois')

with tab7:
    df['day'] = df['date_heure'].dt.day
    create_line_chart(df, 'day', 'Nombre d\'accidents par jour')

with tab8:
    df['dayofweek'] = df['date_heure'].dt.dayofweek
    df['dayofweek'] = df['dayofweek'].replace({
        0: 'Lundi',
        1: 'Mardi',
        2: 'Mercredi',
        3: 'Jeudi',
        4: 'Vendredi',
        5: 'Samedi',
        6: 'Dimanche'
    })
    df['dayofweek'] = pd.Categorical(df['dayofweek'], categories=[
        'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], ordered=True)
    create_line_chart(df, 'dayofweek', 'Nombre d\'accidents par jour de la semaine')

with tab9:
    df['hour'] = df['date_heure'].dt.hour
    create_line_chart(df, 'hour', 'Nombre d\'accidents par heure')

tab1, tab2, tab3, tab4 = st.tabs(['Situation', 'Gravité', 'Route', 'Collision'])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        create_pie_chart(df, 'agglomeration', 'Accidents par zone de circulation')
    with col2:
        create_pie_chart(df, 'meteo', 'Accidents par météo')
    with col3:
        df['éclairage'] = df['éclairage'].replace({
            'Nuit avec éclairage public allumé': 'Nuit avec éclairage',
            'Nuit sans éclairage public': 'Nuit sans éclairage',
            'Nuit avec éclairage public non allumé': 'Nuit sans éclairage'
        })
        create_pie_chart(df, 'éclairage', 'Accidents par luminosité')

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        create_pie_chart(df, 'gravite', 'Accidents par gravité')
    with col2:
        df_filtered = df[df['sexe'] != 'Non renseigné']
        severity_by_age_group = df_filtered.groupby('sexe')['gravite'].value_counts().unstack().reset_index()
        fig = px.bar(
            severity_by_age_group,
            x='sexe',
            y=['Indemne', 'Blessé léger', 'Blessé hospitalisé', 'Tué'],
            title='Gravité des accidents par sexe',
            labels={'value': 'Nombre d\'accidents', 'sexe': 'Sexe'},
            text_auto=True
        )
        fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        bins = [0, 18, 30, 40, 50, 60, 70, 80, 90, 100]
        labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']
        df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
        severity_by_age_group = df.groupby('age_group')['gravite'].value_counts().unstack().reset_index()
        fig = px.bar(
            severity_by_age_group,
            x='age_group',
            y=['Indemne', 'Blessé léger', 'Blessé hospitalisé', 'Tué'],
            title='Gravité des accidents par tranches d\'âges',
            labels={'value': 'Nombre d\'accidents', 'age_group': 'Tranches d\'âges'},
            text_auto=True
        )
        fig.update_layout(title={'x': 0.5, 'xanchor': 'center'}, showlegend=False)
        fig.update_xaxes(categoryarray=labels)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2, col3 = st.columns(3)
    with col1:
        create_pie_chart(df, 'trajet', 'Accidents par type de trajet')
    with col2:
        create_pie_chart(df, 'voie_speciale', 'Présence de voie spéciale pour vélo')
    with col3:
        df_filtered['intersection'] = df['intersection'].replace('Intersection à plus de 4 branches', 'Plus de 4 branches')
        create_pie_chart(df_filtered, 'intersection', 'Accidents par type d\'intersection')

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        create_pie_chart(df, 'collision', 'Accidents par type de collision')
    with col2:
        severity_by_collision = df.groupby('collision')['gravite'].value_counts().unstack().reset_index()
        fig = px.bar(
            severity_by_collision,
            x='collision',
            y=['Indemne', 'Blessé léger', 'Blessé hospitalisé', 'Tué'],
            title='Gravité des accidents par type de collision',
            labels={'value': 'Nombre d\'accidents', 'collision': 'Type de collision'},
            text_auto=True
        )
        fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig, use_container_width=True)
