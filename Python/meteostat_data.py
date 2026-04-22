from datetime import datetime
from meteostat import Daily

# #Downloading meteostat data

# for year in range(2010, 2025):
#     start = datetime(year, 1, 1)
#     end   = datetime(year, 12, 31)

#     station_id = 'FAJB0'
#     name = 'Roosevelt Park'

#     #Daily data
#     data = Daily(station_id, start, end)
#     df = data.fetch()

#     print(df.head())
#     df.to_csv(f'data/Stationsdaten/{station_id}_{name}/{station_id}_{year}_daily.csv')

#______________________________________
#edit csv to standardised - hourly data 
import os
import pandas as pd

def meteostat_processed(year, id, name, lat, lon, elevation):
    path = f'data/Stationsdaten/raw_data/{id}_{name}/{id}_{year}_hourly.csv'
    out_path = f'data/Stationsdaten/processed_data/{id}_{name}/{id}_{name}_{year}.csv'

    if not os.path.exists(path):
            print(f"⚠️ File not found for year {year}, skipping.")
            return
    
    df = pd.read_csv(path)

    df = df[['time', 'temp', 'dwpt', 'rhum', 'wdir', 'wspd']].copy()

    #Editing Date and Time
    df[['DATE','TIME']] = df['time'].astype(str).str.split(' ', expand=True)
    df['TIME'] = df['TIME'].fillna('00:00:00')

    #Clearing unrealistic values
    df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
    df['dwpt'] = pd.to_numeric(df['dwpt'], errors='coerce')
    df['rhum'] = pd.to_numeric(df['rhum'], errors='coerce')
    df.loc[(df['temp'] < -15) | (df['temp'] > 50), 'temp'] = None
    df.loc[(df['dwpt'] < -35) | (df['dwpt'] > 40), 'dwpt'] = None
    df.loc[(df['rhum'] < 0) | (df['rhum'] > 100), 'dwpt'] = None

    #Renaming variables        
    df['TEMP2'] = df['temp']
    df['DEW2'] = df['dwpt']
    df['RHUM2'] = df['rhum']

    df['LAT'] = float(lat)
    df['LON'] = float(lon)
    df['ELEVATION'] = float(elevation)

    #final columns sorted
    df_out = df[['DATE', 'TIME', 'LAT', 'LON', 'ELEVATION', 'TEMP2', 'DEW2', 'RHUM2']]

    # In neue CSV schreiben
    df_out.to_csv(out_path, index=False)
    print(f"✅ {year} processed → {out_path}")

# for year in range(1990, 2025):
#      meteostat_processed(year, 'FAGC0', 'Glen_Austin', -25.9833, 28.15, 1585.83)