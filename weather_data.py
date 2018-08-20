#! /usr/bin/env python3
from datetime import datetime, timedelta
import time  
from collections import namedtuple  
import pandas as pd
import numpy as np
import requests  
import os

from utils import my_logger

logger = my_logger(__name__, level="DEBUG")
try:
    root_path = os.path.dirname(os.path.abspath(__file__))
except:
    root_path = '/Users/lichong/Sources/RPi_weather'


class WeatherData(object):
    """
    历史气象数据获取和预处理，生成训练和测试数据集dataset
    """
    # Weather Underground API
    # API_KEY: The API_KEY that Weather Underground provides with your account
    # YYYYMMDD: A string representing the target date of your request
    # STATE: The two letter state abbreviation in the United States
    # CITY: The name of the city associated with the state you requested
    BASE_URL = 'http://api.wunderground.com/api/{API_KEY}/history_{YYYYMMDD}/q/{STATE}/{CITY}.json'
    API_KEY =  'dcfae7a1de117e98'
    STATE = '上海市'
    CITY = 'Guangfulin'
    URL = 'http://api.wunderground.com/api/dcfae7a1de117e98/history_{YYYYMMDD}/q/上海市/Guangfulin.json'
    FEATURES = ['datetime', 'tempm', 'hum', 'pressurem','conds']
    DailyObservation = namedtuple("DailyObservation", FEATURES)
    # HAZARDOUS_WEATHER = [''.join(['Heavy ', w]) for w in ['Rain', 'Snow',
    #     'Mist', 'Hail', 'Ice', 'Thunderstorm','Freezing']]
    HAZARDOUS_WEATHER = ['Rain', 'Snow', 'Mist', 'Hail', 'Ice', 'Thunderstorm','Freezing']

    def __init__(self, data='data.csv'):
        data_ = data.replace('.csv', '')
        data_cleaned = data_ + '_cleaned.csv'
        dataset = data_ + '_dataset.csv'
        self.data = os.path.join(root_path, data)
        self.data_cleaned = os.path.join(root_path, data_cleaned)
        self.dataset = os.path.join(root_path, dataset)
        self.df = pd.read_csv(self.data, index_col=0, parse_dates=True)
        self.features = ['tempm', 'hum', 'pressurem']
        self.result = 'hazardous'

        self.clean_data()
        self.split_dataset()
            
    def collect_data(self, end_date, days):  
        records = []
        for _ in range(days):
            url = WeatherData.URL.format(
                YYYYMMDD=end_date.strftime('%Y%m%d'))
            response = requests.get(url)
            if response.status_code == 200:
                logger.debug('response success!')
                observations = response.json()['history']['observations']
                # 48 observs each day, twice an hour
                for obv in observations:
                    dt = obv['date']
                    dtt = ''.join(
                        [dt['year'], dt['mon'], dt['mday'],
                        dt['hour'], dt['min']])
                    daily_obv = WeatherData.DailyObservation(
                        datetime=datetime.strptime(dtt, '%Y%m%d%H%M'),
                        tempm=obv['tempm'],
                        hum=obv['hum'],
                        pressurem=obv['pressurem'],
                        conds=obv['conds'])
                    records.append(daily_obv)
            time.sleep(6)
            end_date += timedelta(days=-1)

        df = pd.DataFrame(records, columns=WeatherData.FEATURES).set_index('datetime')  
        df.to_csv(self.data)
        self.df = df
        return records

    def clean_data(self):        
        df = self.df.copy()
        # remove abnormal value [-9999, -999, 'Null', 'N/A']
        xvalues = df[self.features]     
        xvalues = xvalues.apply(pd.to_numeric, errors='coerce')
        xvalues = xvalues.replace(-9999, np.nan)
        xvalues = xvalues.replace(-999, np.nan)
        df[self.features] = xvalues

        # remove unknown tree condition
        df['conds'] = df['conds'].str.strip().str.lower().replace('unknown', np.nan)
        # drop all np.nan
        df = df.dropna()

        # sort index, index is datetime, sort ascending
        df = df.sort_index()

        df.to_csv(self.data_cleaned)
        self.df = df
        return df

    def add_features(self, priors=2, features=None):
        """ add 2 prior samples as the extra features of the current sample. """
        df = self.df.copy()
        if not features:
            features = self.features.copy()
        rows = df.shape[0]
        # derive_nth_day_feature
        for N in range(1, priors+1):
            for feature in features:
                col_name = "{}_{}".format(feature, N)
                df[col_name] = [np.nan]*N + [df[feature][i-N] for i in range(N, rows)]
                self.features.append(col_name)
        # rearrange columns order
        df = df[self.features + ['conds']]
        df = df.dropna()
        self.df = df
        return df

    def split_dataset(self):
        from sklearn.model_selection import train_test_split 
        df = self.df.copy()
        # add a result column 'hazardous'
        hazardous_pattern = '|'.join(WeatherData.HAZARDOUS_WEATHER).lower()
        df[self.result] = df['conds'].str.contains(hazardous_pattern)
        self.X = df[self.features]
        self.y = df[self.result]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=12)
        df.to_csv(self.dataset)
        self.df = df



