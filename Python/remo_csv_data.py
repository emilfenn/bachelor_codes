import pandas as pd
import numpy as np

#remo data from Kelvin to Celsius
def remo_convert_C_and_time(station, year, month):
    #downloaded remo data from levante
    path = (f'data/temp2_{year}{month:02d}_{station}.csv')

    ds_remo = pd.read_csv(path)

    #Convert K to °C
    ds_remo['TEMP2'] = ds_remo['TEMP2'] - 273.15

    #remo time fraction to DATE, TIME
    ds_remo["DATE"] = ds_remo["time"].astype(str).str.split(".").str[0]
    ds_remo["fraction"] = ds_remo["time"] - ds_remo["time"].astype(int)
    minutes = (ds_remo["fraction"] * 24 * 60).round().astype(int)
    ds_remo["TIME"] = pd.to_datetime(minutes, unit="m").dt.strftime("%H:%M")
    ds_remo["DATE"] = pd.to_datetime(ds_remo["DATE"], format="%Y%m%d")

    ds_remo = ds_remo.drop(columns=["fraction"])
    ds_remo = ds_remo.drop(columns=["time"])

    #structure of csv output
    ds_out = ds_remo[['DATE', 'TIME', 'rlon', 'rlat', 'height2m', 'lon', 'lat', 'TEMP2']]

    #print(ds_remo)
    ds_out.to_csv(f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}{month:02d}_{station}_C.csv', index=False)

for month in range (1, 13):
    remo_convert_C_and_time('Jabavu', 2019, month)

#____________________________________________
#concatenate monthly to yearly data

def month_to_year(station, year):

    ds = []
    
    for month in range (1, 13):
        path = (f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}{month:02d}_{station}_C.csv')

        ds.append(pd.read_csv(path))

    yearly_ds = pd.concat(ds, ignore_index=True)

    path_out = (f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')

    yearly_ds.to_csv(path_out, index=False)

    print('Concatenated to yearly file')

    return

month_to_year('Jabavu', 2019)

#________________________________________
#add remo elevation to matching remo csv

def add_elevation(station, year, elevation):
    path = (f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')

    ds = pd.read_csv(path)

    ds['ELEVATION'] = elevation

    path_out = (f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')

    ds.to_csv(path_out, index=False)

    print(f'Elevation: {elevation}m added to station: {station}')

add_elevation('Jabavu', 2019, 1628.8)   #⚠️ Choose matching elevation from remo elevation .nc file ⚠️

#_______________________________________

#change remo elevation to station elevation and calculate height corrected temperature records
def remo_elevation_to_station(station, year):
    ds_remo = pd.read_csv(f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')
    ds_station = pd.read_csv(f'data/Stationsdaten/processed_data/{station}/{station}_{year}.csv')

    lapse_rate = -0.65
    station_elev = ds_station['ELEVATION'].iloc[0]
    remo_elev = ds_remo['ELEVATION'].iloc[0]

    delta_h = station_elev - remo_elev

    ds_remo['ELEVATION_HC'] = station_elev
    ds_remo['TEMP2_HC'] = ds_remo['TEMP2'] + (delta_h / 100) * lapse_rate

    path_out = (f'data/Stationsdaten/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')

    ds_remo.to_csv(path_out, index=False)

    print('Height correction and corrected TEMP2 added')

remo_elevation_to_station('Jabavu', 2019)