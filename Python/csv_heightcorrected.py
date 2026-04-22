import pandas as pd
import os

#Change observed station elevation to rural reference station
def station_heightcorrection(station, year):

    path = (f'data/processed_data/{station}/{station}_{year}.csv')

    if not os.path.exists(path):
        print(f"⚠️ File not found for year {year}, skipping.")
        return
    
    ds_station = pd.read_csv(path)

    target_elevation = 1376.78    #LANSERIA NOAA station elevation
    lapse_rate = -0.65            #mean lapse rate -0.65K/100m

    delta_h = target_elevation - ds_station['ELEVATION']

    ds_station['ELEVATION_RURAL'] = target_elevation
    ds_station['TEMP2_RURAL'] = ds_station['TEMP2'] + (delta_h / 100) * lapse_rate

    path_out = (f'data/processed_data/{station}/{station}_{year}_rural.csv')

    ds_station.to_csv(path_out, index=False)

    print(f'{station} {year} was height corrected and saved')

#for year in range (2019, 2025):
#    station_heightcorrection('Bedfordview', year)

#______________________________________________

#change Remo data to rural reference elevation
def station_heightcorrection(station, year):

    ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')

    target_elevation = 1376.78    #LANSERIA NOAA station elevation
    lapse_rate = -0.65            #mean lapse rate -0.65K/100m

    delta_h = target_elevation - ds_remo['ELEVATION']

    ds_remo['ELEVATION_RURAL'] = target_elevation
    ds_remo['TEMP2_RURAL'] = ds_remo['TEMP2'] + (delta_h / 100) * lapse_rate

    path_out = (f'data/remo/TEMP2/{station}/temp2_{year}_{station}_rural.csv')

    ds_remo.to_csv(path_out, index=False)

    print(f'{station} {year} was height corrected and saved')

for year in range (2014, 2015):
    station_heightcorrection('FAGC0_Glen_Austin', year)
