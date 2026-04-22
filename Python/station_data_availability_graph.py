import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

#----------------------------
#Graph showing available data of stations with daily/hourly records
#----------------------------

#-----------------
# Set Up
#-----------------
data_root = "data/processed_data/"
stations = ["JOH_INT", "LANSERIA", "PRET_IRENE", "Alexandra", "Bedfordview", "Buccleugh", "Davidsonville", "Diepkloof", "Diepsloot", "Glen_Austin", "Ivory_Park", "Jabavu", "Orange_Farm", "FAGC0_Glen_Austin", "Roosevelt_Park"]

#Adjust timeframe
start = pd.Timestamp("2010-01-01")
end   = pd.Timestamp("2024-12-31")
all_days = pd.date_range(start, end, freq="D")
n_days = len(all_days)
n_stations = len(stations)

#records per day to count as "available" day
min_meas_per_day = 1

#Renaming the stations for the plot
station_display_map = {
    "JOH_INT": "JOH_INT (NOAA)",
    "LANSERIA": "Lanseria (NOAA)",
    "PRET_IRENE": "Pretoria–Irene (NOAA)",
    "Alexandra": "Alexandra (SAAQIS)",
    "Bedfordview": "Bedfordview (SAAQIS)",
    "Buccleugh": "Buccleugh (SAAQIS)",
    "Davidsonville": "Davidsonville (SAAQIS)",
    "Diepkloof": "Diepkloof (SAAQIS)",
    "Diepsloot": "Diepsloot (SAAQIS)",
    "Glen_Austin": "Glen Austin 2 (SAAQIS)",
    "Ivory_Park": "Ivory Park (SAAQIS)",
    "Jabavu": "Jabavu (SAAQIS)",
    "Orange_Farm": "Orange Farm (SAAQIS)",
    "FAGC0_Glen_Austin": "Glen Austin (Meteostat)",
    "Roosevelt_Park": "Roosevelt Park (Meteostat)"
}

display_names = [station_display_map.get(s, s) for s in stations]

#------------------------
#Function to build matrix
#------------------------

def build_availability_matrix(data_root, stations, start, end, min_meas_per_day): 

    all_days = pd.date_range(start, end, freq="D")
    n_days = len(all_days)
    n_stations = len(stations)

    #create matrix
    matrix = np.zeros((n_stations, n_days), dtype=np.uint8)

    for i, station in enumerate(stations):
        station_folder = os.path.join(data_root, station)

        if not os.path.isdir(station_folder):
            print(f"⚠️ {station_folder} not found, continue.")
            continue

        for fname in os.listdir(station_folder):
            if not fname.lower().endswith(f".csv"):
                continue

            fpath = os.path.join(station_folder, fname)

            #Reading variables
            try:
                df = pd.read_csv(fpath, usecols=["DATE", "TIME", "TEMP2"])
            except Exception:
                try:
                    df = pd.read_csv(fpath, usecols=["DATE", "TEMP2"])
                except Exception as e:
                    print(f"Error while reading variables {fpath}: {e}")
                    continue

            if "TIME" in df.columns:
                df["TIME"] = df["TIME"].fillna("00:00:00")
                datetimes = pd.to_datetime(
                    df["DATE"].astype(str).str.strip()
                    + " "
                    + df["TIME"].astype(str).str.strip(),
                    errors="coerce"
                )
            else:
                datetimes = pd.to_datetime(
                    df["DATE"].astype(str).str.strip(),
                    errors="coerce"
                )

            
            df["TEMP2"] = pd.to_numeric(df["TEMP2"], errors="coerce")

            #masking for coexisting time and temp2 values
            mask = datetimes.notna() & df["TEMP2"].notna()
            datetimes_valid = datetimes[mask]

            if datetimes_valid.empty:
                continue

            #counting TEMP2 records per day
            days = datetimes_valid.dt.normalize()
            counts = days.value_counts()

            for day_ts, cnt in counts.items():
                if cnt >= min_meas_per_day and start <= day_ts <= end:
                    j = (day_ts - start).days
                    matrix[i, j] = 1

    #----------------------
    #Plot
    #----------------------
    fig, ax = plt.subplots(figsize=(11, max(6, n_stations*0.4)))

    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["indianred", "limegreen"])
    im = ax.imshow(matrix, aspect='auto', interpolation='nearest',
                origin='lower', cmap=cmap)
    

    legend_elements = [
        Patch(facecolor="limegreen",  edgecolor="black", label="≥ 1 record"),
        Patch(facecolor="indianred", edgecolor="black", label="missing day")
        ]

    ax.legend(handles=legend_elements, loc="upper right", frameon=True)

    ax.set_yticks(np.arange(n_stations))
    ax.set_yticklabels(display_names)

    years = list(range(start.year, end.year + 1))
    year_ticks = [ (pd.Timestamp(f"{y}-01-01") - start).days for y in years ]
    ax.set_xticks(year_ticks)
    ax.set_xticklabels(years, ha="left")

    #ax.set_title("Daily temperature data availability per station")

    for xt in year_ticks:
        ax.axvline(xt - 0.5, color='black', linewidth=0.5, alpha=0.6)

    plt.tight_layout()
    #plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Data/data_availability.png', dpi=300)
    plt.show()

    return matrix, all_days

#---------------
#Calling function
matrix, all_days = build_availability_matrix(data_root, stations, start, end, min_meas_per_day)