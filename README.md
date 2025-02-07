# GeoNoise

Niniejsze repozytorium zawiera projekt realizowany na potrzeby kursu **Przetwarzanie danych przestrzennych**. Dotyczy on predykcji poziomu hałasu na podstawie danych przestrzennych miasta Praga, wykorzystując do tego konwolucyjne sieci neuronowe. Dane zostały zebrane ze strony **https://geoportalpraha.cz/**, oraz **https://www.openstreetmap.org/**. 

### Uruchomienie

1. Zainstaluj odpowiednie biblioteki

```
pip install -r requirements.txt
```

2. Aby pobrać i zagregować odpowiednio dane wpisz kolejno

```
   make load_data && make preprocess_data && make aggregate_data && make convert_to_tensor
```

3. W celu treningu i ewaluacji modelu wpisz

```
  make train_eval && make test
```

4. Generowanie interaktywnej mapy do pliku HTML

```
make create_map
```

Eksploracyjna analiza danych jest przedstawiona w formie jupyter notebooków w folderze **notebooks**.
Wyniki modelu są przedstawione w folderze **model**.
