import numpy as np
import pandas as pd
from src.utils import filter_poligon



def noise_basic_stats(noise_data, districts_data):
    all_districts_noise_stats = []

    for i, row in districts_data.iterrows():
        subnoise, subdistrict = filter_poligon(noise_data, districts_data, row['NAZEV_MC'])
        subnoise['area'] = subnoise.geometry.area

        avg_noise = np.average(subnoise['DB_LO'], weights = subnoise['area'])
        sd_noise = np.sqrt(np.average((subnoise['DB_LO'] - avg_noise)**2, weights = subnoise['area']))
        
        # Function to calculate weighted quantile
        def weighted_quantile(values, quantiles, sample_weight):
            sorter = np.argsort(values)
            values = values[sorter]
            sample_weight = sample_weight[sorter]
            weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
            weighted_quantiles /= np.sum(sample_weight)
            return np.interp(quantiles, weighted_quantiles, values)
        
        median_noise = weighted_quantile(subnoise['DB_LO'], 0.50, subnoise['area'])
        min_noise = np.min(subnoise['DB_LO'])
        max_noise = np.max(subnoise['DB_LO'])
        q25_noise = weighted_quantile(subnoise['DB_LO'], 0.25, subnoise['area'])
        q75_noise = weighted_quantile(subnoise['DB_LO'], 0.75, subnoise['area'])
        
        stats_dict = {
            'District': row['NAZEV_MC'],
            'Mean': avg_noise, 
            'Std': sd_noise, 
            'Min': min_noise, 
            'Q25': q25_noise, 
            'Median': median_noise, 
            'Q75': q75_noise, 
            'Max': max_noise
        }
        all_districts_noise_stats.append(stats_dict)

    stats = pd.DataFrame(all_districts_noise_stats)
    
    return stats