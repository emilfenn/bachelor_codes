import matplotlib.pyplot as plt
import pandas as pd

#______________________________________________________________

#Calculating Mean daily UHI for Observations and REMO for multiple years
def annual_UHI_obs_vs_remo(station, year):

    #observational data
    lan_obs = pd.read_csv(f'data/processed_data/LANSERIA/LANSERIA_{year}.csv')
    sta_obs = pd.read_csv(f'data/processed_data/{station}/{station}_{year}_rural.csv')

    lan_obs["datetime"] = pd.to_datetime(lan_obs["DATE"].astype(str) + " " + lan_obs["TIME"])
    sta_obs["datetime"] = pd.to_datetime(sta_obs["DATE"].astype(str) + " " + sta_obs["TIME"])

    # convert to local time
    lan_obs["datetime"] = lan_obs["datetime"] + pd.Timedelta(hours=2)
    sta_obs["datetime"] = sta_obs["datetime"] + pd.Timedelta(hours=2)

    # keep full hours
    lan_obs = lan_obs[(lan_obs["datetime"].dt.minute == 0) & (lan_obs["datetime"].dt.second == 0)]
    sta_obs = sta_obs[(sta_obs["datetime"].dt.minute == 0) & (sta_obs["datetime"].dt.second == 0)]

    lan_obs = lan_obs[["datetime","TEMP2"]].rename(columns={"TEMP2":"T_LANSERIA"})
    sta_obs = sta_obs[["datetime","TEMP2_RURAL"]].rename(columns={"TEMP2_RURAL":"T_URBAN"})

    #aligning observational data
    df_obs = pd.merge(lan_obs, sta_obs, on="datetime", how="inner").dropna()

    # daily means
    daily_obs = (df_obs.set_index("datetime").resample("D").mean().dropna())

    #UHI
    daily_obs["UHI"] = daily_obs["T_URBAN"] - daily_obs["T_LANSERIA"]

    obs_UHI_mean = daily_obs["UHI"].mean()

    # timestamps used
    obs_times = df_obs["datetime"]

    # ----------------------------

    # REMO data
    lan_remo = pd.read_csv(f'data/remo/TEMP2/LANSERIA/temp2_{year}_LANSERIA_C.csv')

    sta_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_rural.csv')

    lan_remo["datetime"] = pd.to_datetime(lan_remo["DATE"].astype(str) + " " + lan_remo["TIME"])
    sta_remo["datetime"] = pd.to_datetime(sta_remo["DATE"].astype(str) + " " + sta_remo["TIME"])

    lan_remo["datetime"] = lan_remo["datetime"] + pd.Timedelta(hours=2)
    sta_remo["datetime"] = sta_remo["datetime"] + pd.Timedelta(hours=2)


    lan_remo = lan_remo[["datetime","TEMP2_HC"]].rename(columns={"TEMP2_HC":"T_LANSERIA"})
    sta_remo = sta_remo[["datetime","TEMP2_RURAL"]].rename(columns={"TEMP2_RURAL":"T_URBAN"})

    #Filtering REMO to observational timestamps
    lan_remo = lan_remo[lan_remo["datetime"].isin(obs_times)]
    sta_remo = sta_remo[sta_remo["datetime"].isin(obs_times)]

    #aligning REMO hours
    df_remo = pd.merge(lan_remo, sta_remo, on="datetime", how="inner").dropna()

    daily_remo = (df_remo.set_index("datetime").resample("D").mean().dropna())

    daily_remo["UHI"] = daily_remo["T_URBAN"] - daily_remo["T_LANSERIA"]

    remo_UHI_mean = daily_remo["UHI"].mean()

    # OUTPUT
    # ----------------------------
    result = {
        "station": station,
        "year": year,
        "UHI_obs_mean": obs_UHI_mean,
        "UHI_remo_mean": remo_UHI_mean,
    }

    return result

results = []

#-------
#CALL

for year in range(2016, 2018):
   results.append(annual_UHI_obs_vs_remo("Diepkloof", year))
df = pd.DataFrame(results)
print(df)

#_______________________________________

#Calculating Mean day- and nighttime UHI for Observations and REMO for multiple years
def annual_UHI_daynight_obs_vs_remo(station, year):

    #observational data
    lan_obs = pd.read_csv(f'data/processed_data/LANSERIA/LANSERIA_{year}.csv')
    sta_obs = pd.read_csv(f'data/processed_data/{station}/{station}_{year}_rural.csv')

    lan_obs["datetime"] = pd.to_datetime(lan_obs["DATE"] + " " + lan_obs["TIME"])
    sta_obs["datetime"] = pd.to_datetime(sta_obs["DATE"] + " " + sta_obs["TIME"])

    lan_obs["datetime"] += pd.Timedelta(hours=2)
    sta_obs["datetime"] += pd.Timedelta(hours=2)

    lan_obs = lan_obs[["datetime","TEMP2"]].rename(columns={"TEMP2":"T_LANSERIA"})
    sta_obs = sta_obs[["datetime","TEMP2_RURAL"]].rename(columns={"TEMP2_RURAL":"T_URBAN"})

    #full hours only
    lan_obs = lan_obs[(lan_obs["datetime"].dt.minute==0) & (lan_obs["datetime"].dt.second==0)]
    sta_obs = sta_obs[(sta_obs["datetime"].dt.minute==0) & (sta_obs["datetime"].dt.second==0)]

    #align observational timestamps
    df_obs = pd.merge(lan_obs, sta_obs, on="datetime", how="inner").dropna()

    df_obs["hour"] = df_obs["datetime"].dt.hour
    df_obs["date"] = df_obs["datetime"].dt.date

    # day/night classification
    df_obs["period"] = df_obs["hour"].apply(lambda h: "day" if 6 <= h < 19 else "night")

    # daily means by period
    daily_obs = (df_obs.groupby(["date","period"])[["T_LANSERIA","T_URBAN"]].mean().reset_index())

    daily_obs["UHI"] = daily_obs["T_URBAN"] - daily_obs["T_LANSERIA"]

    obs_means = daily_obs.groupby("period")["UHI"].mean()

    # timestamps used
    obs_times = df_obs["datetime"]

    #REMO data
    lan_remo = pd.read_csv(f'data/remo/TEMP2/LANSERIA/temp2_{year}_LANSERIA_C.csv')

    sta_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_rural.csv')

    lan_remo["datetime"] = pd.to_datetime(lan_remo["DATE"] + " " + lan_remo["TIME"])
    sta_remo["datetime"] = pd.to_datetime(sta_remo["DATE"] + " " + sta_remo["TIME"])

    lan_remo["datetime"] += pd.Timedelta(hours=2)
    sta_remo["datetime"] += pd.Timedelta(hours=2)

    lan_remo = lan_remo[["datetime","TEMP2_HC"]].rename(columns={"TEMP2_HC":"T_LANSERIA"})
    sta_remo = sta_remo[["datetime","TEMP2_RURAL"]].rename(columns={"TEMP2_RURAL":"T_URBAN"})

    #filtering remo times to obs timestamps
    lan_remo = lan_remo[lan_remo["datetime"].isin(obs_times)]
    sta_remo = sta_remo[sta_remo["datetime"].isin(obs_times)]

    df_remo = pd.merge(lan_remo, sta_remo, on="datetime", how="inner").dropna()

    df_remo["hour"] = df_remo["datetime"].dt.hour
    df_remo["date"] = df_remo["datetime"].dt.date

    df_remo["period"] = df_remo["hour"].apply(lambda h: "day" if 6 <= h < 19 else "night")


    # daily means by period
    daily_remo = (df_remo.groupby(["date","period"])[["T_LANSERIA","T_URBAN"]].mean().reset_index())

    daily_remo["UHI"] = daily_remo["T_URBAN"] - daily_remo["T_LANSERIA"]

    remo_means = daily_remo.groupby("period")["UHI"].mean()

    # OUTPUT
    # ----------------------------
    result = {
        "station": station,
        "year": year,

        "UHI_day_obs": obs_means.get("day", None),
        "UHI_night_obs": obs_means.get("night", None),

        "UHI_day_remo": remo_means.get("day", None),
        "UHI_night_remo": remo_means.get("night", None),

        "n_days_obs": daily_obs["date"].nunique(),
        "n_days_remo": daily_remo["date"].nunique()
    }

    return result

results = []

#---------
#CALL

# for year in range(2014, 2015):
#    results.append(annual_UHI_daynight_obs_vs_remo("FAGC0_Glen_Austin", year))
# df = pd.DataFrame(results)
# print(df)

#_______________________________________     

#Compare Diurnal UHI cycle of any observational stations
def UHI_diurnal_cycle_observations(stations, start_year, end_year):

    #rural reference
    lan_list = []

    for year in range(start_year, end_year + 1):

        lan = pd.read_csv(f'data/processed_data/LANSERIA/LANSERIA_{year}.csv')

        lan_list.append(lan)

    lan = pd.concat(lan_list, ignore_index=True)

    lan["datetime"] = pd.to_datetime(lan["DATE"].astype(str) + " " + lan["TIME"].astype(str), errors="coerce")

    lan["datetime"] = lan["datetime"] - pd.Timedelta(hours=-2)
    lan = lan[lan["datetime"].dt.minute == 0]
    lan["hour"] = lan["datetime"].dt.hour

    lan = lan[["datetime", "hour", "TEMP2"]]

    # Plot layout
    fig, ax = plt.subplots(figsize=(10, 5), sharey=True)

    # Loop over stations
    for station in stations:

        #observation data
        sta_obs_list = []

        for year in range(start_year, end_year + 1):

            try:
                sta = pd.read_csv(f'data/processed_data/{station}/{station}_{year}_rural.csv')
            except FileNotFoundError:
                continue

            sta_obs_list.append(sta)

        if len(sta_obs_list) == 0:
            print(f"no OBS data for {station}")
            continue

        sta_obs = pd.concat(sta_obs_list, ignore_index=True)

        sta_obs["datetime"] = pd.to_datetime(sta_obs["DATE"].astype(str) + " " + sta_obs["TIME"].astype(str), errors="coerce")

        sta_obs["datetime"] = sta_obs["datetime"] - pd.Timedelta(hours=-2)
        sta_obs = sta_obs[sta_obs["datetime"].dt.minute == 0]
        sta_obs["hour"] = sta_obs["datetime"].dt.hour

        sta_obs = sta_obs[["datetime", "hour", "TEMP2_RURAL"]]

        #Observation UHI
        uhi_obs = sta_obs.merge(lan, on=["datetime", "hour"], how="inner")

        uhi_obs["UHI"] = uhi_obs["TEMP2_RURAL"] - uhi_obs["TEMP2"]

        uhi_obs_diurnal = uhi_obs.groupby("hour")["UHI"].mean()

        ax.plot(
            uhi_obs_diurnal.index,
            uhi_obs_diurnal.values,
            label=station
        )

    #-----------------
    #PLOT
    #-----------------
    
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel("Local Time (UTC+2)")
    ax.grid(True)

    ax.set_ylabel("UHI (°C)")

    ax.set_title(f"UHI diurnal cycle – Observations ({start_year}-{end_year})")

    ax.legend()

    plt.tight_layout()
    #plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Results/UHI_diurnal_cycle.png', dpi=300)
    plt.show()

# --------------------
# Call

# UHI_diurnal_cycle_observations(
#     stations=["JOH_INT", "Diepkloof", "Jabavu", "Diepsloot", "Alexandra", "Bedfordview", "Buccleugh", "Orange_Farm", "Roosevelt_Park"],
#     #stations=["Alexandra"],
#     start_year=2014,
#     end_year=2020
# )

#____________________________________________________

#Naming stations for next plot
station_display_names = {
    "JOH_INT": "JOH INT",
    "Bedfordview": "Bedfordview",
    "Diepkloof": "Diepkloof",
    "Diepsloot": "Diepsloot",
    "Jabavu": "Jabavu",
    "Roosevelt_Park": "Roosevelt Park",
}

#Compare Diurnal UHI cycle of any observational and REMO stations
def station_UHI_cycle_multi_v2(stations, start_year, end_year):

    #observational rural reference
    lan_obs_list = []

    for year in range(start_year, end_year + 1):

        lan = pd.read_csv(f'data/processed_data/LANSERIA/LANSERIA_{year}.csv')

        lan_obs_list.append(lan)

    lan_obs = pd.concat(lan_obs_list, ignore_index=True)

    lan_obs["datetime"] = pd.to_datetime(lan_obs["DATE"].astype(str) + " " + lan_obs["TIME"].astype(str),errors="coerce")

    lan_obs["datetime"] = lan_obs["datetime"] - pd.Timedelta(hours=-2)
    lan_obs = lan_obs[lan_obs["datetime"].dt.minute == 0]
    lan_obs["hour"] = lan_obs["datetime"].dt.hour

    lan_obs = lan_obs[["datetime", "hour", "TEMP2"]]
    lan_obs = lan_obs.rename(columns={"TEMP2": "TEMP2_RURAL"})


    #rural reference REMO grid cell data
    lan_remo_list = []

    for year in range(start_year, end_year + 1):

        try:
            lan = pd.read_csv(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Stationsdaten/remo/TEMP2/LANSERIA/temp2_{year}_LANSERIA_rural.csv')
        except FileNotFoundError:
            continue

        lan_remo_list.append(lan)

    lan_remo = pd.concat(lan_remo_list, ignore_index=True)

    lan_remo["datetime"] = pd.to_datetime(lan_remo["DATE"].astype(str) + " " + lan_remo["TIME"].astype(str),errors="coerce")

    lan_remo["datetime"] = lan_remo["datetime"] + pd.Timedelta(hours=2)
    lan_remo = lan_remo[lan_remo["datetime"].dt.minute == 0]
    lan_remo["hour"] = lan_remo["datetime"].dt.hour

    lan_remo = lan_remo[["datetime", "hour", "TEMP2"]]
    lan_remo = lan_remo.rename(columns={"TEMP2": "TEMP2_RURAL"})


    # -----------------------------
    # PLOT
    # -----------------------------
    fig, ax = plt.subplots(1, 2, figsize=(14, 5), sharey=True)


    for station in stations:

        #observation urban station
        sta_obs_list = []

        for year in range(start_year, end_year + 1):

            try:
                sta = pd.read_csv(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Stationsdaten/processed_data/{station}/{station}_{year}_rural.csv')
            except FileNotFoundError:
                continue

            sta_obs_list.append(sta)

        if len(sta_obs_list) == 0:
            print(f"No obs data for {station}")
            continue

        sta_obs = pd.concat(sta_obs_list, ignore_index=True)

        sta_obs["datetime"] = pd.to_datetime(sta_obs["DATE"].astype(str) + " " + sta_obs["TIME"].astype(str),errors="coerce")

        sta_obs["datetime"] = sta_obs["datetime"] - pd.Timedelta(hours=-2)
        sta_obs = sta_obs[sta_obs["datetime"].dt.minute == 0]
        sta_obs["hour"] = sta_obs["datetime"].dt.hour

        sta_obs = sta_obs[["datetime", "hour", "TEMP2_RURAL"]]
        sta_obs = sta_obs.rename(columns={"TEMP2_RURAL": "TEMP2_URBAN"})

        #Observation UHI
        uhi_obs = sta_obs.merge(lan_obs, on=["datetime", "hour"], how="inner")

        if len(uhi_obs) == 0:
            print(f"No overlapping OBS timestamps for {station}")
            continue

        uhi_obs["UHI"] = uhi_obs["TEMP2_URBAN"] - uhi_obs["TEMP2_RURAL"]

        # store timestamps for REMO filtering
        obs_times = uhi_obs["datetime"]

        uhi_obs_diurnal = uhi_obs.groupby("hour")["UHI"].mean()

        ax[0].plot(uhi_obs_diurnal.index,uhi_obs_diurnal.values,label=station_display_names.get(station, station))


        #REMO urban station data
        sta_remo_list = []

        for year in range(start_year, end_year + 1):

            try:
                sta = pd.read_csv(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Stationsdaten/remo/TEMP2/{station}/temp2_{year}_{station}_rural.csv')
            except FileNotFoundError:
                continue

            sta_remo_list.append(sta)

        if len(sta_remo_list) == 0:
            print(f"No REMO data for {station}")
            continue

        sta_remo = pd.concat(sta_remo_list, ignore_index=True)

        sta_remo["datetime"] = pd.to_datetime(sta_remo["DATE"].astype(str) + " " + sta_remo["TIME"].astype(str),errors="coerce")

        sta_remo["datetime"] = sta_remo["datetime"] + pd.Timedelta(hours=2)
        sta_remo = sta_remo[sta_remo["datetime"].dt.minute == 0]
        sta_remo["hour"] = sta_remo["datetime"].dt.hour

        sta_remo = sta_remo[["datetime", "hour", "TEMP2_RURAL"]]
        sta_remo = sta_remo.rename(columns={"TEMP2_RURAL": "TEMP2_URBAN"})


        #Filtering REMO to observational timestamps
        sta_remo = sta_remo[sta_remo["datetime"].isin(obs_times)]
        lan_remo_filtered = lan_remo[lan_remo["datetime"].isin(obs_times)]

        #REMO UHI
        uhi_remo = sta_remo.merge(lan_remo_filtered,on=["datetime", "hour"],how="inner")

        if len(uhi_remo) == 0:
            print(f"No overlapping REMO timestamps for {station}")
            continue

        uhi_remo["UHI"] = uhi_remo["TEMP2_URBAN"] - uhi_remo["TEMP2_RURAL"]

        uhi_remo_diurnal = uhi_remo.groupby("hour")["UHI"].mean()

        ax[1].plot(uhi_remo_diurnal.index,uhi_remo_diurnal.values,label=station_display_names.get(station, station))


    #---------------
    #Plotting

    for a in ax:
        a.axhline(0, color="black", linestyle="--", linewidth=1)
        a.set_xticks(range(0, 24, 2))
        a.set_xlabel("Local Time (UTC+2)")
        a.grid(True)

    ax[0].set_ylabel("UHI (°C)")

    #plt.suptitle(f"UHI Diurnal Cycle ({start_year}–{end_year})", y=0.92)
    ax[0].set_title(f"Observations", fontsize=14)
    ax[1].set_title(f"REMO", fontsize=14)
    handles, labels = ax[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.48, 0.87), ncol=1, framealpha=1)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    #plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Results/UHI_diurnal_cycle.png', dpi=300)
    plt.show()

#----------
#Calling function

# station_UHI_cycle_multi_v2(
#     #stations=["JOH_INT", "Diepkloof", "Jabavu", "Alexandra", "Bedfordview", "Buccleugh", "Roosevelt_Park"],
#     stations=["JOH_INT", "Bedfordview", "Diepkloof", "Diepsloot", "Jabavu", "Roosevelt_Park"],
#     #stations=["Bedfordview"],
#     start_year=2014,
#     end_year=2019
# )