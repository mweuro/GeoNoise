import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.utils import filter_poligon


def noise_density_plot(noise_data):
    _, axs = plt.subplots(1, 1, figsize=(8, 4))
    noise = noise_data.copy()
    noise['area'] = noise.geometry.area
    noise['density'] = noise['area'] / noise['area'].sum()
    sns.barplot(data = noise, x = 'DB_LO', y = 'density', color = 'teal', edgecolor = 'black', ax = axs)
    plt.title("Noise level density", fontsize = 14)
    plt.xlabel("Noise level [dB]", fontsize = 9)
    plt.ylabel("Noise level frequency", fontsize = 9)
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.show()


def districts_noise_density_plot(noise_data, districts_data, *args):
    _, axs = plt.subplots(2, len(args), figsize=(12, 8))
    
    if len(args) == 1:
        axs = [axs]
        
    colors = sns.color_palette('Pastel1', len(args))
    districts = districts_data[districts_data['NAZEV_MC'].isin(args)]
    
    for i, (_, row) in enumerate(districts.iterrows()):
        subnoise, _ = filter_poligon(noise_data, districts_data, row['NAZEV_MC'])
        subnoise['area'] = subnoise.geometry.area
        subnoise['density'] = subnoise['area'] / subnoise['area'].sum()
        sns.barplot(data = subnoise, x = 'DB_LO', y = 'density', color = colors[i], edgecolor = 'black', ax = axs[0][i])
        axs[0][i].set_title(f"{row['NAZEV_MC']} noise density", fontsize = 14)
        axs[0][i].set_xlabel("Noise level [dB]", fontsize = 9)
        axs[0][i].set_ylabel("Noise level frequency", fontsize = 9)
        axs[0][i].tick_params(axis = 'x', rotation = 45)
        districts_data.plot(
            edgecolor = "black",
            color = colors[i],
            linewidth = 1,
            alpha = 0.15,
            ax = axs[1][i],
        )
        districts_data[districts_data['NAZEV_MC'] == row['NAZEV_MC']].plot(
            edgecolor = "black",
            color = colors[i],
            linewidth = 1,
            alpha = 1,
            ax = axs[1][i],
        )
        axs[1][i].set_axis_off()
        
    plt.tight_layout()
    plt.show()