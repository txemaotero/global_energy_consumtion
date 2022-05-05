import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import geopandas

@st.cache
def load_energy_data():
    interesting_values = [
        "population",
        "electricity_generation",
        "renewables_electricity",
        "fossil_electricity",
    ]
    # Load file
    df_energy = pd.read_csv("./data/energy_data.csv")
    # Get interesting columns
    df_energy = df_energy[["country", "iso_code", "year"] + interesting_values]
    # Remove rows with continents and unexisting countries.
    df_energy = df_energy[pd.notna(df_energy["iso_code"])]
    df_energy["renew_perc"] = (
        df_energy["renewables_electricity"] / df_energy["electricity_generation"]
    )
    df_energy["fossil_perc"] = (
        df_energy["fossil_electricity"] / df_energy["electricity_generation"]
    )
    df_energy["elect_percap"] = (
        df_energy["electricity_generation"] / df_energy["population"] * 1000000
    )  # In MWh/person
    return df_energy


if __name__ == "__main__":
    # Load map countries and energy data

    df_energy = load_energy_data()


    world = geopandas.read_file(
        geopandas.datasets.get_path("naturalearth_lowres")
    ).to_crs("EPSG:4326")
    # Sidebar
    interesting_values = {
        "Population": "population",
        "Elect. Generation": "electricity_generation",
        "Renewables Elect.": "renewables_electricity",
        "Renewables %": "renew_perc",
        "Fossil Elect.": "fossil_electricity",
        "Fossil %": "fossil_perc",
        "Elect. per Cap.": "elect_percap",
    }
    with st.sidebar:
        title = st.markdown("## Options:")
        year = st.slider("Year", min_value=1990, max_value=2019, step=1, value=2019)
        to_plot_label = st.radio('Magnitude', interesting_values.keys())

    # TODO: Country filter
    # Body
    st.title("World energy consumption")

    ren_ener = df_energy[
        (df_energy["country"] != "World") & (df_energy["year"] == year)
    ]
    ren_ener.rename(columns={"iso_code": "iso_a3"}, inplace=True)

    merged = world.merge(ren_ener, on="iso_a3").set_index("iso_a3")

    fig = px.choropleth_mapbox(
        merged,
        geojson=merged.geometry,
        locations=merged.index,
        color=interesting_values[to_plot_label],
        mapbox_style="open-street-map",
        zoom=0.3,
        color_continuous_scale='Viridis',
        custom_data=[merged['country'], merged[interesting_values[to_plot_label]]],
        labels={interesting_values[to_plot_label]: to_plot_label},
        opacity=0.8
    )
    temp = "Country: %{customdata[0]}<br>"
    temp += to_plot_label + ": %{customdata[1]}"
    fig.update_traces(
        hovertemplate=temp
    )

    st.subheader("Mapa")
    st.plotly_chart(fig)
