from datetime import datetime, timedelta  
import time  
from collections import namedtuple  
import pandas as pd
import numpy as np
import requests  
import os

from utils import my_logger

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))


class WeatherData(object):
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
        self.data_cleaned = os.path.join(
            root_path, data_cleaned)
        self.dataset = os.path.join(root_path, dataset)

        self.df = pd.read_csv(self.data, index_col=0, parse_dates=True)
        self.features = ['tempm', 'hum', 'pressurem']
        self.result = 'hazardous'
            
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

        # remove unknown weather condition
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
        return

    def logistic_regression(self):
        from sklearn.linear_model import LogisticRegression  
        # instantiate the classifier
        clf = LogisticRegression(random_state=42, max_iter=100)

        # trainning
        clf.fit(self.X_train, self.y_train)

        # make a prediction set using the test set
        prediction = clf.predict(self.X_test)

        # Evaluate the prediction accuracy of the model
        from sklearn.metrics import mean_absolute_error, median_absolute_error  
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))  
        # print("The Mean Absolute Error: %.2f degrees celsius" %
        #     mean_absolute_error(self.y_test, prediction))  
        # print("The Median Absolute Error: %.2f degrees celsius" %
        #     median_absolute_error(self.y_test, prediction))  

    def knn(self):
        from sklearn.neighbors import KNeighborsClassifier
        n_neighbors = 15
        # weights = 'uniform'
        weights = 'distance'
        # we create an instance of Neighbours Classifier and fit the data.
        clf = KNeighborsClassifier(n_neighbors, weights=weights)
        clf.fit(self.X_train, self.y_train)
        prediction = clf.predict(self.X_test)
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))  
    

    def svm(self):
        from sklearn import svm
        clf = svm.SVC(gamma=0.001, C=100.)
        clf.fit(self.X_train, self.y_train)
        prediction = clf.predict(self.X_test)
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))  
        

    def rnn(self):
        from sklearn.model_selection import train_test_split 
        
        # split dataset into training(80%), validation(10%), testing(10%)
        X_train, X_tmp, y_train, y_tmp = train_test_split(
            self.X, self.y, test_size=0.2, random_state=23)
        X_val, X_test, y_val, y_test = train_test_split(
            X_tmp, y_tmp, test_size=0.5, random_state=23)
        print("Training instances   {}, Training features   {}".format(X_train.shape[0], X_train.shape[1]))  
        print("Validation instances {}, Validation features {}".format(X_val.shape[0], X_val.shape[1]))  
        print("Testing instances    {}, Testing features    {}".format(X_test.shape[0], X_test.shape[1]))

    #
    # def tree(self):
    #     from sklearn import tree
    #
    #     # Assumed you have, X (predictor) and Y (target) for training data set and x_test(predictor) of test_dataset
    #     # Create tree object
    #     model = tree.DecisionTreeClassifier(
    #         criterion='gini')  # for classification, here you can change the algorithm as gini or entropy (information gain) by default it is gini
    #
    #     # model = tree.DecisionTreeRegressor() for regression
    #     # Train the model using the training sets and check score
    #     model.fit(X, y)
    #     model.score(X, y)
    #
    #     # Predict Output
    #     predicted = model.predict(x_test)
    




if __name__ == '__main__':
    wd = WeatherData()
    wd.clean_data()
    # wd.add_features()
    wd.split_dataset()
    # wd.logistic_regression()
    wd.rnn()
