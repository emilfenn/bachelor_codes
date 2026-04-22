import pandas as pd

#basic remo statistics for one year
def remo_statistics(station, year):
    #path = (f'data/remo/TEMP2/{station}/temp2_{year}01_{station}_C.csv')   #monthly data
    path = (f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')      #yearly data

    ds_remo = pd.read_csv(path)
    #statistics
    remo_mean = ds_remo['TEMP2'].mean()
    remo_min = ds_remo['TEMP2'].min()
    remo_max = ds_remo['TEMP2'].max()

    print(f"REMO mean: {remo_mean}, min: {remo_min}, max: {remo_max}")

#remo_statistics('JOH_INT', 2015)
#__________________________________________________

#basic station statistics for one year
def station_statistics(station, year):
    #check against station data
    ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')

    ds_station['datetime'] = pd.to_datetime(ds_station['DATE'] + " " + ds_station['TIME'])

    station_mean = ds_station['TEMP2'].mean()
    station_min = ds_station['TEMP2'].min()
    station_max = ds_station['TEMP2'].max()

    print(f"Station mean: {station_mean}, min: {station_min}, max: {station_max}")

#station_statistics('JOH_INT', 2015)

#___________________________________________________
import matplotlib.pyplot as plt

#Comparing monthly temperature diurnal cycle of two files
#Plot 1 shows average over the month
#Plot 2 shows every day in the month
def month_diurnal_cycle(station, year, month):
 
    ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}{month:02d}_{station}_C.csv')                             
    ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')
    #for comparing two obsvervation files
    #ds_remo = pd.read_csv('data/processed_data/Roosevelt_Park/Roosevelt_Park_2015.csv')

    ds_remo["datetime"] = pd.to_datetime(ds_remo["DATE"].astype(str) + " " + ds_remo["TIME"])
    ds_station["datetime"] = pd.to_datetime(ds_station["DATE"].astype(str) + " " + ds_station["TIME"])

    #selecting month and only full hours
    ds_station = ds_station[ds_station["datetime"].dt.month == month] 
    ds_remo = ds_remo[ds_remo["datetime"].dt.month == month]

    #correct to UTC+2
    ds_station["datetime"] = ds_station["datetime"] - pd.Timedelta(hours=-2)      
    ds_remo["datetime"] = ds_remo["datetime"] - pd.Timedelta(hours=-2)

    ds_station["hour"] = ds_station["datetime"].dt.hour
    ds_remo["hour"] = ds_remo["datetime"].dt.hour

    merged = pd.merge(
        ds_station,
        ds_remo,
        on="datetime",
        suffixes=("_station", "_remo")
    )

    print(f"Matching timestamps: {len(merged)}") 

    merged["hour"] = merged["datetime"].dt.hour

    station_diurnal = merged.groupby("hour")["TEMP2_station"].mean()
    remo_diurnal = ds_remo.groupby("hour")["TEMP2"].mean()      

    # Plot
    plt.figure(figsize=(10, 5))

    plt.plot(station_diurnal.index, station_diurnal.values,
             color="blue", marker="o", label="station")

    plt.plot(remo_diurnal.index, remo_diurnal.values,
             color="red", marker="o", label="model")       

    plt.xlabel("Time of day")
    plt.ylabel("Temperature [°C]")
    plt.title(f"Station: {station} diurnal cycle, month {month}, {year}")
    plt.grid(True)
    plt.legend()
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.show()

    # 2. Plot
    plt.figure(figsize=(10, 5))

    plt.plot(merged["datetime"], merged["TEMP2_station"], label="station", color="blue")
    plt.plot(merged["datetime"], merged["TEMP2_remo"], label="model", color="red")

    plt.xlabel("Time of day")
    plt.ylabel("Temperature [°C]")
    plt.title(f"Station: {station} vs. model – month {month}, {year}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

#month_diurnal_cycle('Jabavu', 2018, 1)  #Input: station, year, month

#_________________________

#seasonal or annual diurnal cycle
def seasonal_cycle(station, year):

    ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')
    ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')

    ds_remo["datetime"] = pd.to_datetime(ds_remo["DATE"].astype(str) + " " + ds_remo["TIME"])
    ds_station["datetime"] = pd.to_datetime(ds_station["DATE"].astype(str) + " " + ds_station["TIME"])

    # ⚠️ Choose season
    #season_months = [12, 1, 2]   # DJF     #⚠️ Function needs to be updated so December is from the past year
    #season_months = [3, 4, 5]  # MAM
    #season_months = [6, 7, 8]  # JJA
    #season_months = [9, 10, 11] # SON
    season_months = range (1, 13)  #year

    ds_station = ds_station[ds_station["datetime"].dt.month.isin(season_months)]
    ds_station = ds_station[ds_station["datetime"].dt.minute == 0]

    ds_remo = ds_remo[ds_remo["datetime"].dt.month.isin(season_months)]
    ds_remo = ds_remo[ds_remo["datetime"].dt.minute == 0]

    #correct to UTC+2
    ds_station["datetime"] = ds_station["datetime"] - pd.Timedelta(hours=-2)
    ds_remo["datetime"] = ds_remo["datetime"] - pd.Timedelta(hours=-2)

    ds_station["hour"] = ds_station["datetime"].dt.hour
    ds_remo["hour"] = ds_remo["datetime"].dt.hour

    #Merge on exact timestamps
    df = pd.merge(ds_station, ds_remo, on='datetime', how='inner')

    #add month
    df['month'] = df['datetime'].dt.month

    # Mean Diurnal cycle
    station_diurnal = ds_station.groupby("hour")["TEMP2"].mean()
    remo_diurnal = ds_remo.groupby("hour")["TEMP2_HC"].mean()

    # Plot
    plt.figure(figsize=(10, 5))

    plt.plot(station_diurnal.index, station_diurnal.values,
             color="blue", marker="o", label="station")

    plt.plot(remo_diurnal.index, remo_diurnal.values,
             color="red", marker="o", label="model")

    plt.xlabel("Time of day")
    plt.ylabel("Temperature [°C]")
    plt.title(f"Mean diurnal cycle\n Station: {station} vs. model {year}")
    plt.grid(True)
    plt.legend()
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.show()

#seasonal_cycle('LANSERIA', 2016)        #⚠️specify season in code and title

#______________________________________

#Naming stations
station_display_names = {
    "JOH_INT": "JOH INT",
    "LANSERIA": "LANSERIA",
    "Alexandra": "Alexandra",
    "Bedfordview": "Bedfordview",
    "Diepkloof": "Diepkloof",
    "Jabavu": "Jabavu",
    "Roosevelt_Park": "Roosevelt Park",
}

#Compare diurnal cycle for multiple stations (Obsvervation vs. REMO) for the whole study period
def annual_temp_cycle_comparison(stations, years, path_station, path_remo):

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    #Observations (Stations)
    #------------------------
    for station in stations:
        all_data = []

        for year in years:
            path = path_station.format(station=station, year=year)
            try:
                df = pd.read_csv(path)
            except FileNotFoundError:
                continue

            df["datetime"] = pd.to_datetime(df["DATE"].astype(str) + " " + df["TIME"].astype(str), errors="coerce")
            df["datetime"] = df["datetime"] + pd.Timedelta(hours=2)  # to local time UTC+2
            df = df[df["datetime"].dt.minute == 0]
            df["hour"] = df["datetime"].dt.hour

            all_data.append(df[["hour", "TEMP2"]])

        if len(all_data) == 0:
            print(f"No data available for {station}")
            continue

        all_df = pd.concat(all_data, ignore_index=True)
        diurnal = all_df.groupby("hour")["TEMP2"].mean()
        axes[0].plot(diurnal.index, diurnal.values, marker="", label=station_display_names.get(station, station))

    axes[0].set_title("Observations", fontsize=14)
    axes[0].set_xlabel("Local Time (UTC+2)")
    axes[0].set_ylabel("Temperature [°C]")
    axes[0].grid(True)
    #axes[0].legend()
    axes[0].set_xticks(range(0, 24, 2))
    
    #REMO
    #-----------------------
    for station in stations:
        all_data = []

        for year in years:
            path = path_remo.format(station=station, year=year)
            try:
                df = pd.read_csv(path)
            except FileNotFoundError:
                continue

            df["datetime"] = pd.to_datetime(df["DATE"].astype(str) + " " + df["TIME"].astype(str), errors="coerce")
            df["datetime"] = df["datetime"] + pd.Timedelta(hours=2)  #to UTC+2
            df = df[df["datetime"].dt.minute == 0]
            df["hour"] = df["datetime"].dt.hour

            all_data.append(df[["hour", "TEMP2"]])

        if len(all_data) == 0:
            print(f"No REMO data available for {station}")
            continue

        all_df = pd.concat(all_data, ignore_index=True)
        diurnal = all_df.groupby("hour")["TEMP2"].mean()
        axes[1].plot(diurnal.index, diurnal.values, marker="", label=station_display_names.get(station, station))

    axes[1].set_title("REMO", fontsize=14)
    axes[1].set_xlabel("Local Time (UTC+2)")
    axes[1].grid(True)
    #axes[1].legend()
    axes[1].set_xticks(range(0, 24, 2))
    #axes[1].set_yticks(range(12, 30, 2))

    #plt.suptitle(f"2m Temperature, Diurnal Cycle ({min(years)}–{max(years)})", y=0.92)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.88), ncol=1, framealpha=1)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    #plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Results/diurnal_cycle_temp2.png', dpi=300)
    plt.show()

#_________________________
#INPUT:

stations = ['JOH_INT', 'LANSERIA', 'Alexandra', 'Bedfordview', 'Diepkloof', 'Jabavu', 'Roosevelt_Park']
years = range(2014, 2020)

annual_temp_cycle_comparison(
    stations,
    years,
    path_station= 'data/processed_data/{station}/{station}_{year}.csv',
    path_remo= 'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv',
)
