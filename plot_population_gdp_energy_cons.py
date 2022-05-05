
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon

import matplotlib
matplotlib.rcParams['font.size'] = 17
matplotlib.rcParams['font.family'] = 'times new roman'

def clean_elect(series):
    elect = series.World
    elect = elect[pd.notna(elect)]
    x = elect.index
    y = elect.values/1e3
    return x, y


def gradient_fill(x, y, fill_color=None, ax=None, **kwargs):
    """
    Plot a line with a linear alpha gradient filled beneath it.
    
    Thanks to: https://stackoverflow.com/questions/29321835/is-it-possible-to-get-color-gradients-under-curve-in-matplotlib

    Parameters
    ----------
    x, y : array-like
        The data values of the line.
    fill_color : a matplotlib color specifier (string, tuple) or None
        The color for the fill. If None, the color of the line will be used.
    ax : a matplotlib Axes instance
        The axes to plot on. If None, the current pyplot axes will be used.
    Additional arguments are passed on to matplotlib's ``plot`` function.

    Returns
    -------
    line : a Line2D instance
        The line plotted.
    im : an AxesImage instance
        The transparent gradient clipped to just the area beneath the curve.
    """
    if ax is None:
        ax = plt.gca()

    line, = ax.plot(x, y, **kwargs)
    if fill_color is None:
        fill_color = line.get_color()

    zorder = line.get_zorder()
    alpha = line.get_alpha()
    alpha = 1.0 if alpha is None else alpha

    z = np.empty((100, 1, 4), dtype=float)
    rgb = mcolors.colorConverter.to_rgb(fill_color)
    z[:, :, :3] = rgb
    z[:, :, -1] = np.linspace(0, alpha, 100)[:, None]

    xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    im = ax.imshow(z, aspect='auto', extent=[xmin, xmax, ymin, ymax],
                   origin='lower', zorder=zorder)

    xy = np.column_stack([x, y])
    xy = np.vstack([[xmin, ymin], xy, [xmax, ymin], [xmin, ymin]])
    clip_path = Polygon(xy, facecolor='none', edgecolor='none', closed=True)
    ax.add_patch(clip_path)
    im.set_clip_path(clip_path)

    ax.autoscale(True)
    return line, im

#### Load energy consumption data
df_energy = pd.read_csv('./data/energy_data.csv')
# Get interesting columns
interesting_values = ['population', 'electricity_generation', 'renewables_electricity', 'fossil_electricity']
df_energy = df_energy[['country', 'iso_code', 'year'] + interesting_values]
# Remove rows with continents, unexisting countries.
df_energy = df_energy[pd.notna(df_energy['iso_code'])]
# Create separated tables pivotting
separated_df = {value: df_energy.pivot(columns='country', index='year', values=value) for value in interesting_values} 

#### Load gdp data
df_gdp = pd.read_csv('./data/gdp.csv', header=2)
df_gdp = df_gdp.drop(columns=['Country Code', 'Indicator Name', 'Indicator Code', 'Unnamed: 66']).set_index('Country Name').T
df_gdp.index = df_gdp.index.astype(int)

#### Representation
fig, axes = plt.subplots(ncols=2, figsize=(12, 6))

# Energy consumption
ax = axes[1]

gradient_fill(*clean_elect(separated_df['electricity_generation']), fill_color='tab:blue', ax=ax, label='Total')
gradient_fill(*clean_elect(separated_df['fossil_electricity']), fill_color='tab:orange', ax=ax, label='Fossil')
gradient_fill(*clean_elect(separated_df['renewables_electricity']), fill_color='tab:green', ax=ax, label='Renewable')

ax.set_ylabel('Electricity Consumption (PWh)', labelpad=10)
ax.set_xlabel('Year')
ax.set_xlim((1990, 2020))
ax.legend()

# GDP and population
ax_pop = axes[0]
ax_gdp = ax_pop.twinx()
(separated_df['population'].World/1e9).plot(ax=ax_pop, color='tab:blue', label='Population')
(df_gdp.World/1e12).plot(ax=ax_gdp, color='tab:orange', label='GDP')

ax_pop.plot([], [], color='tab:orange', label='GDP')

ax_pop.set_xlabel('Year')
ax_gdp.set_ylabel('GDP (Trillion USD)', rotation=270, labelpad=20)
ax_pop.set_ylabel('Population (Billion)', labelpad=10)
ax_gdp.set_ylim((0.1, 100))
ax_gdp.set_xlim((1900, 2020))
ax_pop.set_xticks(range(1900, 2021, 20))
ax_pop.legend()

# Separate and save
plt.tight_layout(pad=3)
fig.savefig('figures/population_gdp.pdf', dpi=300)