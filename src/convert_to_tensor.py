import torch
import geopandas as gpd
import pandas as pd
import os
import glob 
import re 


def transform_to_tensor(filepath):
    gdf = gpd.read_file(filepath)
    df = gdf.drop(columns=['geometry'])
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0).astype('float32')
    tensor = torch.tensor(df.values.reshape(26, 25, 7))
    tensor[0] = tensor[0].flip(dims=[0])
    tensor = tensor.flip(dims=[0])
    return tensor    



def main():
    geojson_files = glob.glob(os.path.join('data/pictures', '*.geojson'))
    files_sorted = sorted(geojson_files, key=lambda x: int(re.search(r"(\d+)", x).group()))

    tensors_list = []
    for file in files_sorted:
        tensor = transform_to_tensor(file)
        tensors_list.append(tensor)

    tensors = torch.stack(tensors_list, dim=0)
    torch.save(tensors, 'data_to_train/tensors.pt')
    

if __name__ == '__main__':
    main()