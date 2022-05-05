import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

# Lets start doing a map plot using plotly and a slider to select the year


@st.cache
def load_energy_data():
    interesting_values = ['population', 'electricity_generation', 'renewables_electricity', 'fossil_electricity']
    # Load file
    df_energy = pd.read_csv('./data/energy_data.csv')
    # Get interesting columns
    df_energy = df_energy[['country', 'iso_code', 'year'] + interesting_values]
    # Remove rows with continents and unexisting countries.
    df_energy = df_energy[pd.notna(df_energy['iso_code'])]
    return df_energy


if __name__ == "__main__":
    st.title('World energy consumption')
    loading_text = st.text('Loading data...')
    df_energy = load_energy_data()
    loading_text.text('Data loaded! (using st.cache)')
    st.subheader('Raw data')
    st.write(df_energy)

    fig = px.choropleth(df_energy, locations="iso_code",
                        color="renewables_electricity", # lifeExp is a column of gapminder
                        hover_name="country", # column to add to hover information
                        color_continuous_scale=px.colors.sequential.Plasma, 
                        animation_frame="year",)


    import geopandas

    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres')).to_crs("EPSG:4326")

    ren_ener = df_energy[(df_energy['country'] != 'World') & (df_energy['year'] == 2015)]
    ren_ener.rename(columns={'iso_code': 'iso_a3'}, inplace=True)

    merged = world.merge(ren_ener, on='iso_a3').set_index('iso_a3')

    fig = px.choropleth_mapbox(merged,
                               geojson=merged.geometry,
                               locations=merged.index,
                               mapbox_style="open-street-map",
                               zoom=1,
                               color="renewables_electricity")

    st.subheader('Mapa')
    st.plotly_chart(fig)
