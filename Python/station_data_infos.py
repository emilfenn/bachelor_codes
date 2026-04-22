import pandas as pd
import os

#Total number of temp records per station/year
def records(station, year):
    path = f'data/processed_data/{station}/{station}_{year}.csv'
    
    dataset = pd.read_csv(path)

    # Count how many valid TEMP2 values exist
    n_temp2 = dataset["TEMP2"].count()   # counts only non-NaN values

    print(f'{year}: {n_temp2}')


years = range(2019, 2020)

#for year in years:
#     records('Orange_Farm', year)

#_____________________________________________-
#Max and Min values in dataset

#basic statistics for one station for multiple years
def min_max_values(station):

    all_data = []

    for year in range(2014, 2020):
        path = f'data/processed_data/{station}/{station}_{year}.csv'

        if not os.path.exists(path):
            print(f"⚠️ File not found for year {year}, skipping.")
            continue

        ds_remo = pd.read_csv(path)

        ds_remo['TEMP2'] = pd.to_numeric(ds_remo['TEMP2'], errors='coerce')

        all_data.append(ds_remo)

    all_data_df = pd.concat(all_data, ignore_index=True)

    tmean_all = all_data_df['TEMP2'].mean()
    tmin_all = all_data_df['TEMP2'].min()
    tmax_all = all_data_df['TEMP2'].max()

    print(f"Mean: {tmean_all:.2f} °C")
    print(f"Min: {tmin_all:.2f} °C")
    print(f"Max: {tmax_all:.2f} °C")

    return tmean_all, tmin_all, tmax_all

#min_max_values('FAGC0_Glen_Austin')

#________________________________________
import matplotlib.pyplot as plt

#Compare annual or seasonal temp diurnal cycle of any two stations
def seasonal_cycle_temp(station1, station2,  year):

    ds_station1 = pd.read_csv(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Stationsdaten/processed_data/{station1}/{station1}_{year}.csv')
    ds_station2 = pd.read_csv(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Stationsdaten/processed_data/{station2}/{station2}_{year}.csv')

    ds_station2["datetime"] = pd.to_datetime(ds_station2["DATE"].astype(str) + " " + ds_station2["TIME"])
    ds_station1["datetime"] = pd.to_datetime(ds_station1["DATE"].astype(str) + " " + ds_station1["TIME"])

    # ⚠️ Choose season
    #season_months = [12, 1, 2]   # DJF     #⚠️ Function needs to be updated so December is from the past year
    #season_months = [3, 4, 5]  # MAM
    #season_months = [6, 7, 8]  # JJA
    #season_months = [9, 10, 11] # SON
    season_months = range (1, 13)  #year

    ds_station1 = ds_station1[ds_station1["datetime"].dt.month.isin(season_months)]
    ds_station1 = ds_station1[ds_station1["datetime"].dt.minute == 0]

    ds_station2 = ds_station2[ds_station2["datetime"].dt.month.isin(season_months)]
    ds_station2 = ds_station2[ds_station2["datetime"].dt.minute == 0]

    #correct to UTC+2
    ds_station1["datetime"] = ds_station1["datetime"] - pd.Timedelta(hours=-2)         
    ds_station2["datetime"] = ds_station2["datetime"] - pd.Timedelta(hours=-2)         

    ds_station1["hour"] = ds_station1["datetime"].dt.hour
    ds_station2["hour"] = ds_station2["datetime"].dt.hour

    # Mean Diurnal cycle
    station1_diurnal = ds_station1.groupby("hour")["TEMP2"].mean()
    station2_diurnal = ds_station2.groupby("hour")["TEMP2"].mean()

    # Plot
    plt.figure(figsize=(10, 5))

    plt.plot(station1_diurnal.index, station1_diurnal.values,
             color="blue", marker="", label=(f'{station1}'))

    plt.plot(station2_diurnal.index, station2_diurnal.values,
             color="red", marker="", label=(f'{station2}'))

    plt.xlabel("Local Time (UTC+2)")
    plt.ylabel("Temperature [°C]")
    plt.title(f"Annual diurnal cycle: {station1} vs. {station2} {year}")
    plt.grid(True)
    plt.legend()
    plt.xticks(range(0, 24, 2))
    plt.tight_layout()
    plt.show()

#seasonal_cycle_temp('PRET_IRENE', 'JOH_INT', 2010)