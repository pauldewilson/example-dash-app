import pandas as pd
import numpy as np
import datetime
import calendar
import os


class DataController:
    """
    Class to handle sourcing and aggregating data.
    The csv inputs are each +6m rows and as such
    pre-aggregation before creating use in Plotly
    is required to minimise load & runtimes
    """

    def __init__(self, download_and_aggr_data=False):
        self.download_and_aggr_data = download_and_aggr_data
        # if download true then the csv files will be download to ./csv_files
        self.data_sources = [{
            'meta': '2019-01 NYC taxi data',
            'url': 'https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2019-01.csv'
        }, {
            'meta': '2020-01 NYC taxi data',
            'url': 'https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2020-01.csv'
        }]
        self.datasource = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'datasource')
        self.df = pd.DataFrame()
        self.df_aggr = pd.DataFrame()
        self.df_lists = dict()
        self.files_loaded = 0
        self._run()

    @staticmethod
    def print_current_step(message="", final=False):
        """
        Prints the current step to the screen to inform user of progress
        """
        print("-" * 100)
        if not final:
            print(message + "...")
        elif final:
            print(message)
            print("-" * 100)

    def _concat_and_save_dfs_to_csv(self):
        """
        concatenates like-dataframes from list_dfs and saves to csv
        """
        for key in self.df_lists.keys():
            concat_df = pd.concat([df for df in self.df_lists[key]])
            output_filename = f'{key}.csv'
            output_dir = os.path.abspath(os.path.dirname(__file__))
            full_filepath = output_dir + '\\' + output_filename
            # ensure keep index since saving a grouped by df
            concat_df.to_csv(full_filepath)
            self.print_current_step(f"file saved: {full_filepath}")

    def _download_and_aggregate(self):
        if self.download_and_aggr_data is True:
            self.print_current_step(
                f"download_and_aggr_data is True (see: main.py __name__ statement)"
                f", loading {len(self.data_sources)} files. Please wait")
            # remove unwanted columns
            for source in self.data_sources:
                # if zeroth file being loaded then inform loading else loading next file
                if self.files_loaded == 0:
                    self.print_current_step(f"Loading file")
                else:
                    self.print_current_step(f"Loading next file")
                # load file with only relevant columns
                self.df = pd.read_csv(source['url'], usecols=[
                    'tpep_pickup_datetime',
                    'tpep_dropoff_datetime',
                    'trip_distance',
                    'passenger_count',
                    'fare_amount',
                    'tip_amount'
                ])
                self.files_loaded = self.files_loaded + 1
                self.print_current_step(f"{self.files_loaded} of {len(self.data_sources)} files loaded")
                # change datetime cols to datetime (pre-inspection identified they were objects)
                self.print_current_step("parsing datetime columns")
                for col in self.df.columns:
                    if 'datetime' in col:
                        self.df[col] = pd.to_datetime(self.df[col])
                # during pre-inspection it appeared irrelevant/erroneous data exists.
                # ex. 2019-01 taxi rides data included trip dates from 2003 and 2088.
                # To clean this out, any data that is less or greater than the start
                # and end of the year-month per the meta tag is going to be removed

                # get year month from meta tag
                year_month = source['meta'][0:7]
                # get first day of the month
                year_month_first_day = datetime.datetime.strptime(year_month, '%Y-%m')
                # get last day of the month
                year_month_last_day = datetime.date(year_month_first_day.year, year_month_first_day.month,
                                                    calendar.monthrange(year_month_first_day.year,
                                                                        year_month_first_day.month)[-1])
                # parse dates as numpy.datetime64 for filtering in pandas
                year_month_first_day = np.datetime64(year_month_first_day)
                year_month_last_day = np.datetime64(year_month_last_day)
                # filter the tpep_pickup_datetime column for any instances outside of the start/end dates
                self.df = self.df.loc[
                          (self.df['tpep_pickup_datetime'] >= year_month_first_day)
                          &
                          (self.df['tpep_pickup_datetime'] <= year_month_last_day), :]
                self.print_current_step("calculating trip durations")
                # calculate trip duration
                self.df['trip_duration'] = self.df['tpep_dropoff_datetime'] - self.df['tpep_pickup_datetime']
                # drop columns no longer required
                self.print_current_step("dropping non required columns")
                cols_to_drop = ['tpep_dropoff_datetime']
                self.df.drop(columns=cols_to_drop, inplace=True)
                # rename tpep_pickup_datetime to more user friendly 'trip_date'
                cols_to_rename = {'tpep_pickup_datetime': 'trip_date'}
                self.df.rename(columns=cols_to_rename, inplace=True)
                # convert from datetime to date only (grouping by date later)
                self.df['trip_date'] = self.df['trip_date'].dt.date
                # aggregate by day, day_name, and mean, median
                self.print_current_step("performing aggregation")
                for group_by_col in ['trip_date']:
                    for aggr_type in ['mean', 'median']:
                        # create respective aggregate df
                        if aggr_type == 'mean':
                            self.df_aggr = self.df.copy().groupby(group_by_col).mean()
                        elif aggr_type == 'median':
                            self.df_aggr = self.df.copy().groupby(group_by_col).median()

                        # use df_lists to generate a list of the various dicts according to their matching types
                        # ex. trip_daymean will append only those dfs which are aggregates of trip_day and mean
                        # the reason for isinstance check is because the key name cannot be both dynamic
                        # and defined earlier
                        dataframe_list_key = f"{group_by_col}_{aggr_type}"
                        if dataframe_list_key in self.df_lists.keys():
                            self.df_lists[dataframe_list_key].append(self.df_aggr)
                        else:
                            self.df_lists[dataframe_list_key] = []
                            self.df_lists[dataframe_list_key].append(self.df_aggr)

                # end of present file, remove initial df from memory
                del self.df

            # merge dataframes from list_dfs and save to csv
            self.print_current_step("Merging dataframes for output")
            self._concat_and_save_dfs_to_csv()
            # end of data load and aggregation
            self.print_current_step(f"FINISHED: {self.files_loaded} of {len(self.data_sources)} files outputed.",
                                    final=True)

    def _run(self):
        """
        If self.download_and_aggr_data then csvs are
        downloaded, aggregated, and saved in this dir
        NOTE: data was inspected before creating this Class
        """
        self._download_and_aggregate()
