import pandas as pd

#Correcting TEMP and DEW values
def correct_values(year):
    path = f'data/Stationsdaten/RAND/{year}_gabs.csv'

    ds = pd.read_csv(path, quotechar='"', low_memory=False)

    for col in ['TMP', 'DEW']:
            if col in ds.columns:
                ds[col] = ds[col].astype(str).str.replace(',', '.', regex=False)
                ds[col] = pd.to_numeric(ds[col], errors='coerce') / 10              #all values divided by 10
                ds[col] = ds[col].round(2)
            else:
                print(f"{year}: Error")

    ds.to_csv(f'data/Stationsdaten/RAND/{year}_corrected.csv', index=False)

    print(f'{year} was corrected and saved')

#for year in range(2014, 2025):
#    correct_values(year)

#______________________________
import os

#Edit csv to standardised format
def noaa_processed(year, name):
    path = f'data/Stationsdaten/processed_data/{name}/{year}_corrected.csv'
    out_path = f'data/Stationsdaten/processed_data/{name}/{name}_{year}.csv'

    if not os.path.exists(path):
            print(f"⚠️ File not found for year {year}, skipping.")
            return
    
    df = pd.read_csv(path)

    df = df[['DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'TMP', 'DEW']].copy()

    #Editing Date and Time
    df[['DATE','TIME']] = df['DATE'].astype(str).str.split('T', expand=True)
    df['TIME'] = df['TIME'].fillna('00:00:00')

    #Clearing unrealistic values
    df['TMP'] = pd.to_numeric(df['TMP'], errors='coerce')
    df['DEW'] = pd.to_numeric(df['DEW'], errors='coerce')
    df.loc[(df['TMP'] < -15) | (df['TMP'] > 50), 'TMP'] = None
    df.loc[(df['DEW'] < -35) | (df['DEW'] > 40), 'DEW'] = None

    #Renaming variables        
    df['TEMP2'] = df['TMP']
    df['DEW2'] = df['DEW']

    # Float-Converting
    df['LAT'] = df['LATITUDE'].astype(float)
    df['LON'] = df['LONGITUDE'].astype(float)
    df['ELEVATION'] = df['ELEVATION'].astype(float)

    #csv structure
    df_out = df[['DATE', 'TIME', 'LAT', 'LON', 'ELEVATION', 'TEMP2', 'DEW2']]

    df_out.to_csv(out_path, index=False)
    print(f"✅ {year} processed → {out_path}")

# for year in range(1990, 2025):
#      noaa_processed(year, 'LANSERIA')