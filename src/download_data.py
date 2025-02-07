import requests
import os
from src.utils import load_yaml

def _download_single_dataset(url: str, output_file: str) -> None:
    response = requests.get(url, stream = True)
    response.raise_for_status()
    with open(output_file, 'wb') as file:
        for chunk in response.iter_content(chunk_size = 8192):
            file.write(chunk)
    return
    
    

def download_data(urls_dict: dict[str, str]) -> None:
    for url, output_file in urls_dict.items():
        try:
            if os.path.exists(output_file) or os.path.exists(output_file.split('.')[0] + '.geojson'):
                print(f'The file {output_file} already exists')
                continue
            else:
                _download_single_dataset(url, output_file)
                print(f'Downloaded the data to {output_file}')
        except requests.exceptions.HTTPError as e:
            print(f'Failed to download the data: {e}')
        finally:
            continue
    print('Download completed')
    return



def main() -> None:
    yaml_path = 'params.yaml'
    urls_dict = load_yaml(yaml_path)['download_data']
    download_data(urls_dict)
    return



if __name__ == '__main__':
    main()