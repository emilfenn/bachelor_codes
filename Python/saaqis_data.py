import pandas as pd
import os

#CONVERT EXCEL TO CSV
#I changed the header information manually in each file

excel_file = 'data/SAAQIS/Orange_Farm_10_07_2019_20_10_2025.xlsx'
csv_file = 'data/SAAQIS/Orange_Farm_10_07_2019_20_10_2025.csv'

#df = pd.read_excel(excel_file)

#read header
#print(df.columns.tolist())

#df.to_csv(csv_file,index=False, encoding="utf-8")

#___________________________________________________
#Edit csv to standardised format

def saaqis_processed(name, start_date, end_date, lat, lon, elevation):
    
    path = f'data/raw_data/SAAQIS/{name}_{start_date}_{end_date}.csv'

    df = pd.read_csv(path)

    df = df[['time', 'temp', 'rhum']].copy()

    #Editing Date and Time
    df[['TIME','DATE_RAW']] = df['time'].str.split(' ', expand=True)
    df['DATE'] = pd.to_datetime(df['DATE_RAW'], format='%d/%m/%Y', errors='coerce')
    df = df[df['DATE'].dt.year <= 2024]
    df['DATE'] = df['DATE'].dt.strftime('%Y-%m-%d')
    df['TIME'] = df['TIME'].fillna('00:00:00')

    #Clearing unrealistic values
    df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
    df['rhum'] = pd.to_numeric(df['rhum'], errors='coerce')
    df.loc[(df['temp'] < -15) | (df['temp'] > 50), 'temp'] = None
    df.loc[(df['rhum'] < 0) | (df['rhum'] > 100), 'rhum'] = None

    #Renaming and adding variables        
    df['TEMP2'] = df['temp']
    df['RHUM2'] = df['rhum']

    df['LAT'] = float(lat)
    df['LON'] = float(lon)
    df['ELEVATION'] = float(elevation)

    #final columns sorted
    df_out = df[['DATE', 'TIME', 'LAT', 'LON', 'ELEVATION', 'TEMP2', 'RHUM2']]

    df_out['YEAR'] = pd.to_datetime(df_out['DATE']).dt.year

    years = sorted(df_out['YEAR'].unique())
    base_out_dir = f'data/processed_data/{name}/'

    for y in years:
        df_year = df_out[df_out['YEAR'] == y].copy()
        out_path_year = os.path.join(base_out_dir, f"{name}_{y}.csv")
        df_year.drop(columns=['YEAR']).to_csv(out_path_year, index=False)
        print(f"Saved: {out_path_year}")

    print(f"Processing complete for station: {name}")


#saaqis_processed('Orange_Farm', '10_07_2019', '20_10_2025', -26.47944, 27.86694, 1579)

#List of SAAQIS Stations, timeframe with data, coordinates, elevation from srtm1 arc second global 30m resolution
#'Alexandra', '01_10_2018', '20_10_2025', -26.10694, 28.11, 1520
#'Bedfordview', '01_11_2018', '27_03_2023', -26.17861, 28.13306, 1629
#'Buccleugh', '18_03_2019', '20_10_2025', -26.04472, 28.09889, 1508
#'Davidsonville', '12_12_2022', '20_10_2025', -26.15417, 27.84944, 1693
#'Diepkloof', '06_12_2011', '22_04_2024', -26.25056, 27.95639, 1716
#'Diepsloot', '02_11_2017', '20_10_2025', -25.92167, 28.01861, 1440
#'Glen_Austin', '01_06_2021', '20_10_2025', -25.96278, 28.17000, 1567
#'Ivory_Park', '01_04_2021', '20_10_2025', -25.99278, 28.20389, 1565
#'Jabavu', '01_06_2016', '20_10_2025', -26.25250, 27.87194, 1619
#'Orange_Farm', '10_07_2019', '20_10_2025', -26.47944, 27.86694, 1579

#________________________________________________
#Correct 24:00 to 00:00

def correct_time(name, year):
    path = f'data/processed_data/{name}/{name}_{year}.csv'

    if not os.path.exists(path):
       print(f"⚠️ File not found for year {year}, skipping.")
       return
    
    df = pd.read_csv(path)

    df["DATE"] = pd.to_datetime(df["DATE"])

    mask_24 = df["TIME"] == "24:00"
    df.loc[mask_24, "DATE"] = df.loc[mask_24, "DATE"] + pd.Timedelta(days=1)
    df.loc[mask_24, "TIME"] = "00:00"

    path_out = f'data/processed_data/{name}/{name}_{year}.csv'
    df.to_csv(path_out, index=False)


#for year in range(2011, 2025):
#    correct_time('Orange_Farm', year)

#___________________________________________
#Convert UTC+2 to UTC+0
import os

def saaqis_to_utc(station, year):

    path = f'data/processed_data/{station}/{station}_{year}.csv'

    if not os.path.exists(path):
            print(f"⚠️ File not found for year {year}, skipping.")
            return

    df = pd.read_csv(path)

    # DATE als datetime
    df["datetime"] = pd.to_datetime(df["DATE"].astype(str) + " " + df["TIME"])

    #convert to UTC+0
    df["datetime"] = df["datetime"] - pd.Timedelta(hours=+2)

    df["DATE"] = df["datetime"].dt.strftime("%Y-%m-%d")
    df["TIME"] = df["datetime"].dt.strftime("%H:%M:%S")

    df = df.iloc[2:, :]
    df = df.drop(columns=["datetime"])

    path_out = f'data/processed_data/{station}/{station}_{year}.csv'
    df.to_csv(path_out, index=False)


#for year in range(2011, 2025):
#    saaqis_to_utc('Orange_Farm', year)