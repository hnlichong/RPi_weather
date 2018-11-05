#! /usr/bin/env python3
import pickle
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
    # 气象站观测的数据特性
    OBS_FEATURES = ['datetime', 'tempm', 'hum', 'pressurem','conds']
    # 数据集的特性
    FEATURES = ['tempm', 'hum', 'pressurem']
    DailyObservation = namedtuple("DailyObservation", OBS_FEATURES)
    # HAZARDOUS_WEATHER = [''.join(['Heavy ', w]) for w in ['Rain', 'Snow',
    #     'Mist', 'Hail', 'Ice', 'Thunderstorm','Freezing']]
    HAZARDOUS_WEATHER = ['Rain', 'Snow', 'Mist', 'Hail', 'Ice', 'Thunderstorm','Freezing']

    def __init__(self, data='data.csv'):
        data_ = data.replace('.csv', '')
        data_cleaned = data_ + '_cleaned.csv'
        self.features = WeatherData.FEATURES
        self.result = 'hazardous'
        self.data = os.path.join(root_path, data)
        self.data_cleaned = os.path.join(root_path, data_cleaned)
        self.df = pd.read_csv(self.data, index_col=0, parse_dates=True)
        self.df = self.clean_data(self.df, self.features)
        self.add_result_column()
        self.df.to_csv(self.data_cleaned)
        self.X = self.df[self.features]
        self.y = self.df[self.result]

    @staticmethod
    def fetch_history_data(end_date, days):
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

        df = pd.DataFrame(records, columns=WeatherData.OBS_FEATURES).set_index('datetime')
        return df

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

        df = pd.DataFrame(records, columns=WeatherData.OBS_FEATURES).set_index('datetime')
        df.to_csv(self.data)
        self.df = df
        return records

    @staticmethod
    def clean_data(df, features):
        df = df.copy()
        # remove abnormal value [-9999, -999, 'Null', 'N/A']
        xvalues = df[features]
        xvalues = xvalues.apply(pd.to_numeric, errors='coerce')
        xvalues = xvalues.replace(-9999, np.nan)
        xvalues = xvalues.replace(-999, np.nan)
        df[features] = xvalues

        # remove unknown tree condition
        df['conds'] = df['conds'].str.strip().str.lower().replace('unknown', np.nan)
        # drop all np.nan
        df = df.dropna()

        # sort index, index is datetime, sort ascending
        df = df.sort_index()

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

    def add_result_column(self):
        df = self.df.copy()
        # add a result column 'hazardous'
        hazardous_pattern = '|'.join(WeatherData.HAZARDOUS_WEATHER).lower()
        df[self.result] = df['conds'].str.contains(hazardous_pattern)
        self.df = df

    @staticmethod
    def history_data_to_csv():
        # get history data
        end_datetime = datetime(2018, 5, 26)
        days = 3
        df = WeatherData.fetch_history_data(end_datetime, days)
        df = WeatherData.clean_data(df, WeatherData.FEATURES)
        # add a result column 'hazardous'
        hazardous_pattern = '|'.join(WeatherData.HAZARDOUS_WEATHER).lower()
        df['hazardous'] = df['conds'].str.contains(hazardous_pattern)
        # write into file
        file_name = end_datetime.strftime('%Y%m%d') + '-' + str(days) + '.csv'
        file_path = os.path.join(root_path, 'history_data', file_name)
        df.to_csv(file_path)

def merge_env_data():
    end_datetime = datetime(2018, 5, 26)
    days = 3
    env_data_dir = os.path.join(root_path, 'env_data')
    # merge and clean env_data
    file_name_list = []
    frames = []
    dt = end_datetime
    for i in range(days):
        file_name = dt.strftime('%Y%m%d')+'.csv'
        file_path = os.path.join(env_data_dir, file_name)
        df = pd.read_csv(file_path, dtype = {'datetime' : str})
        # df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d%H%M%S')
        # df.set_index('datetime')
        # 只取每个半小时的数据(分钟: 00，30)
        df = df[df['datetime'].str.contains(r'\d{10}(00|30)\d{2}')]
        # 舍弃秒
        df['datetime'] = df['datetime'].str.slice(0, -2)
        frames.append(df)
        dt += timedelta(days=-1)
    df = pd.concat(frames)
    # 修正温度、湿度: 温度-7.8℃，湿度+10%。
    df['temperature(℃)'] = df['temperature(℃)'] - 7.8
    df['humidity(%)'] = df['humidity(%)'] + 10
    # 转datetime为index
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d%H%M')
    df = df.set_index('datetime')
    # 加入气象站数据
    file_name = end_datetime.strftime('%Y%m%d') + '-' + str(days) + '.csv'
    file_path = os.path.join(root_path, 'history_data', file_name)
    his_df = pd.read_csv(file_path)
    his_df['datetime'] = pd.to_datetime(his_df['datetime'])
    his_df = his_df.set_index('datetime')
    res_df = df.join(his_df, on='datetime')
    # 去掉NA，气象站数据有些半小时记录没有
    res_df = res_df.dropna()
    # 重排列列，便于比较
    cols = ['temperature(℃)', 'tempm', 'humidity(%)', 'hum', 'pressure(mbar)', 'pressurem', 'pred_hazardous', 'hazardous', 'conds']
    res_df = res_df.ix[:, cols]
    # 按时间先后重排列
    res_df = res_df.sort_index()
    # 计算env_data的预测值pred_hazardous
    with open('/Users/lichong/sources/RPi_weather/knn.pickle', 'rb') as fr:
        clf = pickle.load(fr)
    X = res_df[['temperature(℃)', 'humidity(%)', 'pressure(mbar)']]
    res_df['pred_hazardous'] = clf.predict(X)
    # 计算预测准确度
    res = sum(res_df['pred_hazardous'] == res_df['hazardous']) / res_df['pred_hazardous'].size
    print('predict accuracy: ', res)
    import ipdb; ipdb.set_trace()



if __name__ == '__main__':
    merge_env_data()


