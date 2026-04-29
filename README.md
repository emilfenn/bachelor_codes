Short explanation of each code used for the analysis in the bachelor thesis: Evaluation of the regional climate model REMO for air temperature and urban heat island simulations in Johannesburg, South Africa (2014 - 2019)
by Emil Fenn
14.06.2026

Data uploaded on zenodo:
https://doi.org/10.5281/zenodo.19692183

Python codes:

1. meteostat_data.py
Downloads Meteostat station data and reformats the raw hourly CSV files into a standardized dataset with cleaned temperature, dew point, humidity, and station metadata for further analysis.

2. NOAA_data.py
Corrects and standardizes NOAA station data by converting raw temperature and dew point values, cleaning invalid entries, extracting date and time, and saving the results in a consistent analysis-ready format.

3. saaqis_data.py
Converts and standardizes SAAQIS station data by cleaning temperature and humidity records, splitting them into yearly files, correcting invalid 24:00 timestamps, and converting local time (UTC+2) to UTC.

4. csv_heightcorrected.py
Applies an elevation correction to temperature data by adjusting values to a common reference height (using a lapse rate), then saves the corrected dataset for further analysis.

5. remo_csv_daty.py
Processes REMO climate model temperature data by converting it from Kelvin to Celsius, converting model time values into date and time, merging monthly files into yearly datasets, adding elevation data, and applying a height correction so temperatures match the station elevation.

6. station_data_infos.py
Counts valid temperature records, calculates overall mean/min/max temperatures across multiple years, and plots the average diurnal temperature cycle to compare two stations.

7. remo_station_comparison.py
Calculates basic temperature statistics and compares observed station data with REMO model data through monthly, seasonal, and multi-station diurnal cycle plots.

8. station_data_availability_graph.py 
Creates a data availability plot showing which stations have valid daily temperature records over time, making it easy to compare coverage and gaps across the full study period.

9. UHI_analysis.py
Calculates and compares urban heat island (UHI) intensity from observations and REMO model data, including annual mean values, day–night differences, and multi-station diurnal cycles.

10. validation_analysis.py
Calculates REMO model performance against station observations using bias, RMSE, and MAE for mean temperature, daily maximum, and daily minimum, and visualizes station-specific bias distributions with boxplots.

jupyter notebook:

1. extract_remo.ipynb
Extracts temperature time series from REMO NetCDF files for the grid cell nearest to a station, processes each monthly file, and saves the results as CSV files.

