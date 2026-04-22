import pandas as pd
import numpy as np

#Calculate the annual mean bias and RMSE of the remo model per station
def Tmean_Bias_RMSE(station, year):

    ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')
    ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')

    #datetime
    ds_station['datetime'] = pd.to_datetime(ds_station['DATE'] + ' ' + ds_station['TIME'], errors='coerce')
    ds_remo['datetime'] = pd.to_datetime(ds_remo['DATE'] + ' ' + ds_remo['TIME'], errors='coerce')

    #Time Correction to UTC+2
    ds_remo["datetime"] = ds_remo["datetime"] - pd.Timedelta(hours=-2)                     
    ds_station["datetime"] = ds_station["datetime"] - pd.Timedelta(hours=-2)                    

    ds_station = ds_station[['datetime', 'TEMP2']].rename(columns={'TEMP2': 'T_obs'})
    ds_remo = ds_remo[['datetime', 'TEMP2_HC']].rename(columns={'TEMP2_HC': 'T_model'})

    #Merge on exact timestamps
    df = pd.merge(ds_station, ds_remo, on='datetime', how='inner')

    #drop non matching records
    df = df.dropna(subset=['T_obs', 'T_model'])

    #add month
    df['month'] = df['datetime'].dt.month

    #difference 
    diff = df['T_model'] - df['T_obs']

    #Mean Bias, RMSE and Mean absolute error
    bias = diff.mean()
    rmse = np.sqrt((diff ** 2).mean())
    mae  = diff.abs().mean()

    # monthly stats
    monthly_stats = (
        df.groupby('month')
          .apply(lambda x: pd.Series({
              'N': len(x),
              'bias_C': (x['T_model'] - x['T_obs']).mean(),
              'rmse_C': np.sqrt(((x['T_model'] - x['T_obs'])**2).mean()),
          }))
    )

    print(f'Station: {station}\nYear: {year}\nBias: {bias:.2f} °C\nRMSE: {rmse:.2f} °C\nMAE: {mae:.2f} °C')
    print(len(df))
    print(monthly_stats)
    
    return {
        'station': station,
        'year': year,
        'N_common_timesteps': len(df),
        'bias_C': bias,
        'rmse_C': rmse,
    }

#Tmean_Bias_RMSE('Roosevelt_Park', 2019)     

#________________________________________________
#Annual Mean Bias and RMSE for Tmax and Tmin

def Tx_Tn_Bias_RMSE(station, year):

    ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')
    ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')

    #datetime
    ds_station['datetime'] = pd.to_datetime(ds_station['DATE'] + ' ' + ds_station['TIME'], errors='coerce')
    ds_remo['datetime'] = pd.to_datetime(ds_remo['DATE'] + ' ' + ds_remo['TIME'], errors='coerce')

    #Time Correction
    ds_remo["datetime"] = ds_remo["datetime"] - pd.Timedelta(hours=-2)                     
    ds_station["datetime"] = ds_station["datetime"] - pd.Timedelta(hours=-2)

    ds_station = ds_station[['datetime', 'TEMP2']].rename(columns={'TEMP2': 'T_obs'})
    ds_remo = ds_remo[['datetime', 'TEMP2_HC']].rename(columns={'TEMP2_HC': 'T_model'})

    # Merge
    df = pd.merge(ds_station, ds_remo, on='datetime', how='inner')
    df = df.dropna(subset=['T_obs', 'T_model'])

    df['date'] = df['datetime'].dt.date

    #Daily Tmax and Tmin
    daily = df.groupby('date').agg(
        T_max_obs=('T_obs', 'max'),
        T_max_model=('T_model', 'max'),
        T_min_obs=('T_obs', 'min'),
        T_min_model=('T_model', 'min')
    )

    #difference for Tmax
    daily['bias_max'] = daily['T_max_model'] - daily['T_max_obs']

    #difference for Tmin
    daily['bias_min'] = daily['T_min_model'] - daily['T_min_obs']

    #Calculate annual mean bias and rmse
    bias_max_mean = daily['bias_max'].mean()
    bias_min_mean = daily['bias_min'].mean()
    rmse_max_mean = np.sqrt(((daily['T_max_model'] - daily['T_max_obs'])**2).mean())
    rmse_min_mean = np.sqrt(((daily['T_min_model'] - daily['T_min_obs'])**2).mean())

    print(f"Station: {station}, Year: {year}")
    print(f"Bias Tmax: {bias_max_mean:.2f} °C, RMSE Tmax: {rmse_max_mean:.2f} °C")
    print(f"Bias Tmin: {bias_min_mean:.2f} °C, RMSE Tmin: {rmse_min_mean:.2f} °C")

    return {
        'station': station,
        'year': year,
        'N_days': len(daily),
        'bias_Tmax_C': bias_max_mean,
        'rmse_Tmax_C': rmse_max_mean,
        'bias_Tmin_C': bias_min_mean,
        'rmse_Tmin_C': rmse_min_mean
    }

Tx_Tn_Bias_RMSE('Alexandra', 2019)


#________________________________________
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

#PLOTS
#Plotting Boxplots for Mean Bias
#all values
#daily Tmax and Tmin

#---------------------------------------------------------
#                         INPUT                          
#---------------------------------------------------------
stations = [
    "JOH_INT",
    "LANSERIA",
    "PRET_IRENE",
    "Alexandra",
    "Bedfordview",
    "Buccleugh",
    "Diepkloof",
    "Diepsloot",
    "Jabavu",
    "Roosevelt_Park",
    "FAGC0_Glen_Austin",
]

stations_labels = {
    "JOH_INT" : "JOH INT\n(D) ",
    "LANSERIA" : "LANSERIA\n(D)",
    "Alexandra" : "Alexandra\n(9)",
    "Bedfordview" : "Bedfordview\n(9)",
    "Buccleugh" : "Buccleugh\n(B)",
    "Diepkloof" : "Diepkloof\n(6)",
    "Diepsloot" : "Diepsloot\n(8)",
    "Jabavu" : "Jabavu\n(9)",
    "Roosevelt_Park" : "Ro. Park\n(6)",
    "FAGC0_Glen_Austin" : "Glen Austin\n(9)",
}

years = range(2014, 2020)

#-----------------------

#Collect all Mean Bias values
def collect_all_diffs(stations, years):

    records = []

    for station in stations:
        for year in years:
            try:
                ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')
                ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')

                ds_station['datetime'] = pd.to_datetime(ds_station['DATE'] + ' ' + ds_station['TIME'], errors='coerce')
                ds_remo['datetime']    = pd.to_datetime(ds_remo['DATE'] + ' ' + ds_remo['TIME'], errors='coerce')

                ds_remo["datetime"]    = ds_remo["datetime"] + pd.Timedelta(hours=2)
                ds_station["datetime"] = ds_station["datetime"] + pd.Timedelta(hours=2)

                ds_station = ds_station[['datetime', 'TEMP2']].rename(columns={'TEMP2': 'T_obs'})
                ds_remo    = ds_remo[['datetime', 'TEMP2_HC']].rename(columns={'TEMP2_HC': 'T_model'})

                df = pd.merge(ds_station, ds_remo, on='datetime', how='inner')
                df = df.dropna(subset=['T_obs', 'T_model'])

                df["diff"] = df["T_model"] - df["T_obs"]
                df["station"] = station

                records.append(df[["station", "diff"]])

            except Exception as e:
                print(f"Skipped {station} {year}: {e}")

    return pd.concat(records, ignore_index=True)

df_all = collect_all_diffs(stations, years)         #save for plotting

#_______________________________________

#Collecting MB values for Tmax and Tmin
def collect_all_daily_tx_tn_bias(stations, years):

    records = []

    for station in stations:
        for year in years:
            try:
                ds_remo = pd.read_csv(f'data/remo/TEMP2/{station}/temp2_{year}_{station}_C.csv')
                ds_station = pd.read_csv(f'data/processed_data/{station}/{station}_{year}.csv')

                ds_station['datetime'] = pd.to_datetime(ds_station['DATE'] + ' ' + ds_station['TIME'], errors='coerce')
                ds_remo['datetime'] = pd.to_datetime(ds_remo['DATE'] + ' ' + ds_remo['TIME'], errors='coerce')

                ds_remo["datetime"]    = ds_remo["datetime"] + pd.Timedelta(hours=2)
                ds_station["datetime"] = ds_station["datetime"] + pd.Timedelta(hours=2)

                ds_station = ds_station[['datetime', 'TEMP2']].rename(columns={'TEMP2': 'T_obs'})
                ds_remo = ds_remo[['datetime', 'TEMP2_HC']].rename(columns={'TEMP2_HC': 'T_model'})

                df = pd.merge(ds_station, ds_remo, on='datetime', how='inner')
                df = df.dropna(subset=['T_obs', 'T_model'])

                df['date'] = df['datetime'].dt.date

                df['date'] = df['datetime'].dt.date

                daily = df.groupby('date').agg( Tmax_obs = ('T_obs', 'max'), Tmax_model = ('T_model', 'max'), Tmin_obs = ('T_obs', 'min'), Tmin_model = ('T_model', 'min') ) 
                out = pd.DataFrame({ "station": station, "bias_Tmax": daily["Tmax_model"] - daily["Tmax_obs"], "bias_Tmin": daily["Tmin_model"] - daily["Tmin_obs"] })

                records.append(out.reset_index(drop=True))

            except Exception as e:
                print(f"Skipped {station} {year}: {e}")

    return pd.concat(records, ignore_index=True)

df_all_tx_tn = collect_all_daily_tx_tn_bias(stations, years)    #safe for plotting

#_______________________________________

#Boxplot Set Up
def plot_bias_all_values_boxplot_mean(ax, df_all, ylabel, title):

    stations = df_all["station"].unique()

    data = []
    means = []
    stations_plot = []

    for s in stations:
        vals = df_all.loc[df_all["station"] == s, "diff"].dropna()

        if vals.empty:
            continue

        mean_val = vals.mean()
        p10 = np.percentile(vals, 10)
        p90 = np.percentile(vals, 90)

        print(f"{stations_labels.get(s,s)}:")
        print(f"  Mean bias = {mean_val:.2f} °C")
        print(f"  P10 = {p10:.2f} °C")
        print(f"  P90 = {p90:.2f} °C")
        print()

        stations_plot.append(stations_labels.get(s, s))
        data.append(vals.values)
        means.append(vals.mean())

    x = np.arange(1, len(stations_plot) + 1)

    #Boxplot
    ax.boxplot(
        data,
        positions=x,
        widths=0.4,
        showfliers=False,
        whis=(10,90),
        patch_artist=True,
        boxprops=dict(facecolor="lightblue", edgecolor="black"),
        medianprops=dict(linewidth=0),   #median not shown
    )

    # Mean Bias as line
    ax.hlines(
        means,
        x - 0.2,
        x + 0.2,
        colors="red",
        linewidth=1,
        zorder=3,
        label='Mean Bias'
    )

    ax.set_xticks(x)
    ax.yaxis.set_major_locator(MultipleLocator(2.5))
    ax.axhline(0,color='black',linestyle='--',linewidth=1,zorder=0)
    #ax.set_yticks(np.arange(-2.5, 13, 2.5))
    ax.set_xticklabels(stations_plot, rotation=0, fontsize= 12)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)


#=================================================
#Plot Mean Bias for all values

fig, ax = plt.subplots(figsize=((14),5))

plot_bias_all_values_boxplot_mean(
    ax,
    df_all,
    ylabel="Bias [°C]",
    title=""
)

#plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Results/bias_temp2.png', dpi=300)  
plt.show()

#=================================================
#PLot Mean Bias for Tmax values

fig, ax = plt.subplots(figsize=((14),5))

plot_bias_all_values_boxplot_mean(
    ax,
    df_all_tx_tn.rename(columns={"bias_Tmax": "diff"}),
    ylabel="Bias [°C]",
    title=""
)

#plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Results/bias_tmax.png', dpi=300)
plt.show()

#=================================================
#Plot Mean Bias for Tmin values

fig, ax = plt.subplots(figsize=((14),5))

plot_bias_all_values_boxplot_mean(
    ax,
    df_all_tx_tn.rename(columns={"bias_Tmin": "diff"}),
    ylabel="Bias [°C]",
    title=""
)

#plt.savefig(f'/Users/emilfenn/Library/CloudStorage/OneDrive-UniversitätHamburg/Studium/WiSe_25-26/Bachelorarbeit/Figures/Results/bias_tmin.png', dpi=300)
plt.show()