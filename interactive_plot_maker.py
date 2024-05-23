#Ref: https://stackoverflow.com/questions/31410043/hiding-lines-after-showing-a-pyplot-figure
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pandas as pd
from mplcursors import cursor
from argparse import RawTextHelpFormatter


def main():
    parser = argparse.ArgumentParser(description="Interactive plot for mean global SST/SSTA.", formatter_class=RawTextHelpFormatter)

    ##### READING IN ARGUMENTS #####
    parser.add_argument(
        '--data_type',
        type=str,
        choices = ['SST', 'SSTA'],
        required=True,
        help="Type of data to plot: SST or SSTA"
    )

    parser.add_argument(
        '--anomaly_type',
        type=str,
        required=False,
        choices = ['FIXED_BASELINE', 'PREV_YEAR_SST', 'ADJACENT_YEARS'],
        help="""Type of anomaly, where SSTA calculated: 
        - 'FIXED_BASELINE': by providing a fixed baseline (--baseline argument needs to be given)
        - 'PREV_YEAR_SST' : based on previous year temperatures (i.e. SST_y - SST_(y-1))
        - 'ADJACENT_YEARS': w.r.t. a baseline calculated using 'n' years on either side 
                            of a particular year (excluding that particular year itself).
        """
    )

    parser.add_argument(
        '--obs_name',
        type=str,
        choices=['HadISST', 'NOAA_OISST'],
        required=True,
        help="Data options are 'HadISST' or 'NOAA_OISST'"
    )
    parser.add_argument(
        '--start_year',
        type=int,
        required=True,
        help="Start year: Any year >= 1982 (for NOAA_OISST) and >= 1870 (for HadISST)"
    )
    parser.add_argument(
        '--end_year',
        type=int,
        required=True,
        help="End year: Any year <= 2023"
    )
    parser.add_argument(
        '--baseline',
        type=str,
        help="Baseline in the format of 'YYYY-YYYY"
    )
    parser.add_argument(
        '--window',
        type=int,
        help="Number of adjacent years to consider to calculate baseline of each year"
    )

    args = parser.parse_args()
    validate_years(args.start_year, args.end_year, args.obs_name) # Validating the arguments based on data available

    if args.obs_name == 'HadISST':
        f = 12 # Time increments in a year; HadISST is available at monthly resolution
        year_range = pd.date_range(start='01-01-2023', end='31-12-2023', freq='MS')
    elif args.obs_name == 'NOAA_OISST':
        f = 365 # Time resolution; NOAA_OISST is available at daily resolution
        year_range = pd.date_range(start='01-01-2023', end='31-12-2023', freq='D')
    '''
    year_range is basically used as the x-axis (month or day of year) of the interactive plot. '2023' is just arbitrarily 
    chosen as year here, you can put any non-leap year (will be removing leap days in next step for ease of analysis).
    '''

    ##### READING IN SST DATA #####
    df = pd.read_csv('./data/'+args.obs_name+'_globmean_sst_data.csv')
    df['TIME'] = pd.to_datetime(df['TIME']) # Making sure TIME column is in datetime format.
    df = df.set_index('TIME') # Setting TIME as index.
    df = df[~((df.index.month == 2) & (df.index.day == 29))] # Removing leap days
    df = df[(df.index.year>=args.start_year) & (df.index.year<=args.end_year)] # Cropping timeperiod based on start and end year given by user.

    ##### UPDATING df BASED ON data_type SELECTED #####
    if args.data_type == 'SSTA':
        df,dtype_title = ssta_calculator(anomaly_type = args.anomaly_type, 
                                         df = df,
                                         start_year = args.start_year,
                                         end_year = args.end_year,
                                         baseline = args.baseline,
                                         window = args.window)
        if args.anomaly_type == 'PREV_YEAR_SST':
            args.start_year += 1
    else:
        dtype_title = 'SST'
    
    nyears = args.end_year - args.start_year + 1 
    # Number of years to reshape df values to (years, f) shape, for calculating mean, mean+2*std & mean-2*std.

    ##### PLOTTING CODE #####
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.set_title(args.obs_name+' | Mean '+dtype_title+' | World 60S-60N | '+str(args.start_year)+'-'+str(args.end_year),
                    fontweight='bold',
                    fontsize=16)
    ax.grid(True)
   
    lines = []
    for i in range(args.start_year, args.end_year + 1):
        line, = ax.plot(year_range, df.loc[df.index.year == i]['SST'], lw=1.5, label=str(i), alpha=0.3)
        lines = lines + [line]

    line, = ax.plot(year_range, np.array(df['SST']).reshape(nyears, f).mean(axis=0), color='black', lw=1.5,
                    label='{}-{} Mean'.format(args.start_year,args.end_year))
    lines = lines + [line]
    line, = ax.plot(year_range, np.array(df['SST']).reshape(nyears, f).mean(axis=0) +
                    2 * np.array(df['SST']).reshape(nyears, f).std(axis=0),
                    '--', label='plus 2σ', color='grey', lw=1.5)
    lines = lines + [line]
    line, = ax.plot(year_range, np.array(df['SST']).reshape(nyears, f).mean(axis=0) -
                    2 * np.array(df['SST']).reshape(nyears, f).std(axis=0),
                    '--', label='minus 2σ', color='grey', lw=1.5)
    lines = lines + [line]

    ax.set_xticks(ticks=[x for x in year_range if (x.day == 1)], labels=['1 Jan', '1 Feb', '1 Mar', '1 Apr',
                                                                            '1 May', '1 Jun', '1 Jul', '1 Aug', '1 Sep',
                                                                            '1 Oct', '1 Nov', '1 Dec'])
    ax.legend(fancybox=True, shadow=True, ncols=12, bbox_to_anchor=(0.5, -0.25), loc="lower center")
    cursor(hover=True)

    leg = interactive_legend()
    return fig, ax, leg


def validate_years(start_year, end_year, obs_name):
    if obs_name == 'NOAA_OISST' and start_year < 1982:
        raise argparse.ArgumentTypeError("start_year must be >= 1982 for NOAA_OISST")
    if obs_name == 'HadISST' and start_year < 1870:
        raise argparse.ArgumentTypeError("start_year must be >= 1870 for HadISST")
    if end_year > 2023:
        raise argparse.ArgumentTypeError("end_year must be <= 2023")
    if start_year > end_year:
        raise argparse.ArgumentTypeError("start_year must be less than or equal to end_year")

def ssta_calculator(anomaly_type, df, start_year, end_year, baseline = None, window = None):
    if anomaly_type == 'FIXED_BASELINE':

        try:
            bs_start, bs_end = [int(x) for x in baseline.split('-')]
            if bs_start > bs_end:
                raise argparse.ArgumentTypeError("Baseline start year must be less than or equal to baseline end year")
        except:
            raise argparse.ArgumentTypeError("Invalid baseline or none given. Baseline must be in the format 'YYYY-YYYY'")

        bs_start, bs_end = [int(x) for x in baseline.split('-')] # Baseline start and end year
        bs_df = df[(df.index.year >= bs_start) & (df.index.year <= bs_end)] # Cropping df to select baseline years only
        climatology = bs_df.groupby([bs_df.index.month, bs_df.index.day]).mean() # Grouping my month and day to get mean climatology

        def get_climatology(row, climatology):
            month, day = row.name.month, row.name.day
            return climatology.loc[(month, day)]
        
        # Making a new row climatological value (calculated from baseline) based on 'day (or month) of year' for each row of the timeseries.
        df['Climatology'] = df.apply(get_climatology, axis=1, climatology=climatology)

        df['SST'] = df['SST'] - df['Climatology'] # Calculating anomaly; ignore the column name still being 'SST'
        df.drop(columns='Climatology', inplace=True)
        dtype_title = 'SSTA (Baseline: '+baseline+')' # Updating the figure title accordingly
    elif anomaly_type == 'PREV_YEAR_SST':
        anom = df.copy(deep = True)
        start_year = start_year + 1 # start_year being updated by 1; need to fix (or improve?) this later.
        for year in range(start_year,end_year+1): # Simple SST_{y} - SST_{y-1}
            anom[anom.index.year == year] = df[df.index.year == year].values - df[df.index.year == (year-1)].values
        df = anom[(anom.index.year>=start_year) & (anom.index.year<=end_year)] # Cropping to just start_year to end_year
        dtype_title = 'SSTA (w.r.t. previous year mean SST)' # Updating the figure title accordingly
    elif anomaly_type == 'ADJACENT_YEARS':
        if window is None:
            raise argparse.ArgumentTypeError("Invalid number of years (i.e. window) or none given.")
        anoms = [] # This will be list of pandas Series objects, each series will be anomaly calculated below for each year.
        for year in range(start_year, end_year+1):
            # Selecting adjacent 'year +/- window' years except for the year itself. This will be our baseline for that particular year.
            bs_df = df[(df.index.year >= year-window) & (df.index.year <= year+window) & (df.index.year != year)]
            # Calculating mean baseline by grouping the bs_df by 'day (or month) of year' and then calculating anomalies
            anoms = anoms + [df[df.index.year == year]['SST'] - bs_df.groupby([bs_df.index.month, bs_df.index.day]).mean()['SST'].values]
        df = pd.concat(anoms).to_frame() # Merging all the individual years' anomalies into a dataframe
        dtype_title = 'SSTA (with adjacent {} years as baseline)'.format(window) # Updating the figure title accordingly
    else:
        raise argparse.ArgumentTypeError("Invalid anomaly_type selected (or no selection made), please check available options")
    return df, dtype_title


def interactive_legend(ax=None):
    if ax is None:
        ax = plt.gca()
    if ax.legend_ is None:
        ax.legend()

    return InteractiveLegend(ax.get_legend())

class InteractiveLegend(object):
    def __init__(self, legend):
        self.legend = legend
        self.fig = legend.axes.figure

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legend_handles:
            artist.set_picker(10) # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self, legend):
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legend_handles
        label2handle = dict(zip(labels, handles))
        handle2text = dict(zip(handles, legend.texts))

        lookup_artist = {}
        lookup_handle = {}
        for artist in legend.axes.get_children():
            if artist.get_label() in labels:
                handle = label2handle[artist.get_label()]
                lookup_handle[artist] = handle
                lookup_artist[handle] = artist
                lookup_artist[handle2text[handle]] = artist

        lookup_handle.update(zip(handles, handles))
        lookup_handle.update(zip(legend.texts, handles))

        return lookup_artist, lookup_handle


    def on_pick(self, event):
        handle = event.artist
        if handle in self.lookup_artist:

            artist = self.lookup_artist[handle]
            artist.set_visible(not artist.get_visible())
            self.update()

    def on_click(self, event):
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lookup_artist.values():
            artist.set_visible(visible)
        self.update()

    def update(self):
        for artist in self.lookup_artist.values():
            handle = self.lookup_handle[artist]
            if artist.get_visible():
                handle.set_visible(True)
            else:
                handle.set_visible(False)
        self.fig.canvas.draw()

    def show(self):
        plt.show()

if __name__ == '__main__':
    fig, ax, leg = main()
    plt.show()