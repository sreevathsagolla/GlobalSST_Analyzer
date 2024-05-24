
# MEAN_SST_PLOTTER [BETA]
An interactive plotter for daily/monthly mean global Sea Surface Temperature (SST). Each year's data is plotted as an individual line, allowing for easy comparison across years.

## Features
- Interactive plotting for mean global SST and SST Anomalies (SSTA).
- Toggle years on and off in the plot for detailed analysis.
- Supports data from HadISST and NOAA_OISST.
- Flexible anomaly calculations with multiple baseline options.

## Data
Area-weighted mean sea surface temperature data from:
- HadISST for 1870-2023 timeperiod at monthly resolution (Bayner et al., 2003)
- NOAA OISST v2.1  for 1982-2023 timeperiod at daily resolution (Huang et al., 2020)

## Usage
To get started, use the following command to see the available options:

```sh
python3 interactive_plot_maker.py --help
```

### Command-Line Options
```
usage: interactive_plot_maker.py [-h] --data_type {SST,SSTA} [--anomaly_type {FIXED_BASELINE,PREV_YEAR_SST,ADJACENT_YEARS}] --obs_name {HadISST,NOAA_OISST} --start_year START_YEAR --end_year END_YEAR [--baseline BASELINE] [--window WINDOW]

Interactive plot for mean global SST/SSTA.

options:
  -h, --help            show this help message and exit
  --data_type {SST,SSTA}
                        Type of data to plot: SST or SSTA
  --anomaly_type {FIXED_BASELINE,PREV_YEAR_SST,ADJACENT_YEARS}
                        Type of anomaly calculation:
                          - 'FIXED_BASELINE': Requires --baseline argument in 'YYYY-YYYY' format.
                          - 'PREV_YEAR_SST': Based on previous year temperatures (SST_y - SST_(y-1)).
                          - 'ADJACENT_YEARS': Baseline calculated using 'n' years on either side of a particular year (excluding the year itself).

  --obs_name {HadISST,NOAA_OISST}
                        Data options: 'HadISST' or 'NOAA_OISST'
  --start_year START_YEAR
                        Start year: >= 1982 (for NOAA_OISST) or >= 1870 (for HadISST)
  --end_year END_YEAR   End year: <= 2023
  --baseline BASELINE   Baseline in 'YYYY-YYYY' format
  --window WINDOW       Number of adjacent years to consider for baseline calculation
```

## Example Usages
Here are some example usages for different anomaly types using `NOAA_OISST` as the `obs_name`, with a `start_year` of 1982 and an `end_year` of 2023:

```sh
# Example 1: Plotting SST (Sea Surface Temperature) without anomalies
python3 interactive_plot_maker.py --data_type SST --obs_name NOAA_OISST --start_year 1982 --end_year 2023

# Example 2: Plotting SSTA (Sea Surface Temperature Anomaly) using a fixed baseline
# Here, the baseline period is set from 1982 to 1991.
python3 interactive_plot_maker.py --data_type SSTA --anomaly_type FIXED_BASELINE --baseline 1982-1991 --obs_name NOAA_OISST --start_year 1982 --end_year 2023

# Example 3: Plotting SSTA using the previous year's SST as the baseline
# This calculates anomalies as the difference between the current year's SST and the previous year's SST.
python3 interactive_plot_maker.py --data_type SSTA --anomaly_type PREV_YEAR_SST --obs_name NOAA_OISST --start_year 1982 --end_year 2023

# Example 4: Plotting SSTA using adjacent years for the baseline
# Here, the 'window' argument specifies the number of adjacent years on either side of the current year to use for the baseline calculation.
# For this example, a window of 5 years is used.
python3 interactive_plot_maker.py --data_type SSTA --anomaly_type ADJACENT_YEARS --window 5 --obs_name NOAA_OISST --start_year 1982 --end_year 2023
```

## Interactive Plot Instructions
- **Right Mouse Button (RMB)**: Toggle off all years.
- **Middle Mouse Button (MMB)**: Toggle on all years.
- **Left click** on a specific year in the legend to toggle that year on/off individually.
- **Hover cursor** to view year and SST or SSTA value at that time of the year. 

## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas or report any bugs.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

Feel free to reach out at sg13n23@soton.ac.uk if you have any questions or need further assistance!