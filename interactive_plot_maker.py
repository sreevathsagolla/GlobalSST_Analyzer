#Ref: https://stackoverflow.com/questions/31410043/hiding-lines-after-showing-a-pyplot-figure
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pandas as pd
from mplcursors import cursor


def main():
    parser = argparse.ArgumentParser(description="Interactive plot for mean global SST/SSTA.")


    parser.add_argument(
        '--data_type',
        type=str,
        required=True,
        help="Type of data: SST, SSTA_1 [w.r.t. first 30yr baseline], SSTA_2 [w.r.t. previous year temperatures i.e. SST_y - SST_(y-1)]"
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
        help="Baseline in the format of 'YYYY-YYYY'"
    )

    args = parser.parse_args()

    data_type, start_year, end_year, obs_name = args.data_type, args.start_year, args.end_year, args.obs_name

    if data_type == 'SSTA_1':
        if args.baseline:
            validate_baseline(args.baseline)
        else:
            raise argparse.ArgumentTypeError("baseline invalid or not given, please retry.")

    validate_years(start_year, end_year, obs_name)

    if obs_name == 'HadISST':
        f = 12
        year_range = pd.date_range(start='01-01-2023', end='31-12-2023', freq='MS')
    elif obs_name == 'NOAA_OISST':
        f = 365
        year_range = pd.date_range(start='01-01-2023', end='31-12-2023', freq='D')


    df = pd.read_csv('./data/'+obs_name+'_globmean_sst_data.csv')
    df['TIME'] = pd.to_datetime(df['TIME'])
    df = df.set_index('TIME')
    df = df[~((df.index.month == 2) & (df.index.day == 29))]
    df = df[(df.index.year>=start_year) & (df.index.year<=end_year)]
    
    if data_type == 'SSTA_1':
        bs_start, bs_end = [int(x) for x in args.baseline.split('-')]
        bs_df = df[(df.index.year >= bs_start) & (df.index.year <= bs_end)]
        climatology = bs_df.groupby([bs_df.index.month, bs_df.index.day]).mean()
        def get_climatology(row, climatology):
            month, day = row.name.month, row.name.day
            return climatology.loc[(month, day)]
        df['Climatology'] = df.apply(get_climatology, axis=1, climatology=climatology)
        df['SST'] = df['SST'] - df['Climatology']
        df.drop(columns='Climatology', inplace=True)
        dtype_title = 'SSTA (Baseline: '+args.baseline+')'
    elif data_type == 'SSTA_2':
        anom = df.copy(deep = True)
        start_year = start_year + 1
        for year in range(start_year,end_year+1):
            anom[anom.index.year == year] = df[df.index.year == year].values - df[df.index.year == (year-1)].values
        df = anom[(anom.index.year>=start_year) & (anom.index.year<=end_year)]
        dtype_title = 'SSTA (w.r.t. previous year mean SST)'
    elif data_type == 'SST':
        dtype_title = 'SST'

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.set_title(obs_name+' | Mean '+dtype_title+' | World 60S-60N | '+str(start_year)+'-'+str(end_year),
                    fontweight='bold',
                    fontsize=16)
    ax.grid(True)
   
    lines = []
    for i in range(start_year, end_year + 1):
        line, = ax.plot(year_range, df.loc[df.index.year == i]['SST'], lw=1.5, label=str(i), alpha=0.3)
        lines = lines + [line]

    line, = ax.plot(year_range, np.array(df['SST']).reshape(end_year-start_year+1, f).mean(axis=0), color='black', lw=1.5,
                    label='{}-{} Mean'.format(start_year,end_year))
    lines = lines + [line]
    line, = ax.plot(year_range, np.array(df['SST']).reshape(end_year-start_year+1, f).mean(axis=0) +
                    2 * np.array(df['SST']).reshape(end_year-start_year+1, f).std(axis=0),
                    '--', label='plus 2σ', color='grey', lw=1.5)
    lines = lines + [line]
    line, = ax.plot(year_range, np.array(df['SST']).reshape(end_year-start_year+1, f).mean(axis=0) -
                    2 * np.array(df['SST']).reshape(end_year-start_year+1, f).std(axis=0),
                    '--', label='minus 2σ', color='grey', lw=1.5)
    lines = lines + [line]

    ax.set_xticks(ticks=[x for x in year_range if (x.day == 1)], labels=['1 Jan', '1 Feb', '1 Mar', '1 Apr',
                                                                            '1 May', '1 Jun', '1 Jul', '1 Aug', '1 Sep',
                                                                            '1 Oct', '1 Nov', '1 Dec'])
    ax.legend(fancybox=True, shadow=True, ncols=12, bbox_to_anchor=(0.5, -0.25), loc="lower center")
    cursor(hover=True)
#    ax.set_ylim(19.8,21.2)

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
    return start_year, end_year

def validate_baseline(baseline):
    try:
        start_baseline, end_baseline = map(int, baseline.split('-'))
        if start_baseline > end_baseline:
            raise argparse.ArgumentTypeError("Baseline start year must be less than or equal to baseline end year")
    except ValueError:
        raise argparse.ArgumentTypeError("Baseline must be in the format 'YYYY-YYYY'")

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