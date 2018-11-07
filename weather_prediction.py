#! /usr/bin/env python3
from inspect import isfunction
from math import exp, sqrt, pi
from numpy import mean, std
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn import tree
import graphviz 
from weather_data import WeatherData
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
import pickle

class Prediction(WeatherData):
    def __init__(self):
        super().__init__()

    def logistic_regression(self):
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

    def logistic_alpha(self):
        res = []
        alphas = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1]
        n = 10
        for alpha in alphas:
            r = []
            for i in range(n):
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    self.X, self.y, test_size=0.2, random_state=12)
                self.clf = LogisticRegression(C=1/alpha)
                self.clf.fit(self.X_train, self.y_train)
                r.append(
                  self.clf.score(self.X_test, self.y_test)
                )
            res.append(sum(r)/len(r))
        # plt.scatter(y[:, 0], y[:, 1], marker='o')
        plt.plot(alphas, res, 'bo-')
        print(res)
        plt.grid(True)
        plt.axis('tight')
        plt.xlabel('alpha')
        plt.ylabel('Test accuracy')
        plt.show()

    def knn(self):
        # we create an instance of Neighbours Classifier and fit the data.
        clf = KNeighborsClassifier(n_neighbors=15, weights='uniform', metric='euclidean')
        clf.fit(self.X_train, self.y_train)
        prediction = clf.predict(self.X_test)
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))

    def knn_k(self):
        res = []
        k_range = range(1, 31)
        n = 10
        for k in k_range:
            r = []
            for i in range(n):
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    self.X, self.y, test_size=0.2, random_state=12)
                self.clf = KNeighborsClassifier(n_neighbors=k, weights='uniform', metric='euclidean')
                self.clf.fit(self.X_train, self.y_train)
                r.append(
                  self.clf.score(self.X_test, self.y_test)
                )
            res.append(sum(r)/len(r))
        # plt.scatter(y[:, 0], y[:, 1], marker='o')
        plt.plot(k_range, res, 'bo-')
        print(res)
        plt.grid(True)
        plt.axis('tight')
        plt.xlabel('K value')
        plt.ylabel('Test accuracy')
        plt.show()

    def knn_metric(self):
        metrics = ['euclidean', 'manhattan', 'chebyshev']
        res = {}
        n = 10
        k = 15
        for met in metrics:
            r = []
            for i in range(n):
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    self.X, self.y, test_size=0.2, random_state=12)
                self.clf = KNeighborsClassifier(n_neighbors=k, weights='uniform', metric=met)
                self.clf.fit(self.X_train, self.y_train)
                r.append(
                    self.clf.score(self.X_test, self.y_test)
                )
            res[met] = sum(r)/len(r)
        print(res)



    def knn_weights(self):
        def minus_equation(li):
            res = []
            for val in li:
                res.append(1-val)
                # if val < 1:
                #     res.append(1-val)
                # else:
                #     res.append(0)
            return res
        def gaussian(xx):
            yy = []
            sigma = std(xx)
            mu = mean(xx)
            for x in xx:
                k = 1 / sigma / sqrt(2 * pi)
                y = k * exp(-pow(x - mu, 2) / 2 / sigma)
                yy.append(y)
            return yy

        weights = ['uniform', 'distance', minus_equation, gaussian]
        res = {}
        n = 10
        for wei in weights:
            r = []
            for i in range(n):
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    self.X, self.y, test_size=0.2, random_state=12)
                self.clf = KNeighborsClassifier(n_neighbors=15, weights=wei, metric='euclidean')
                self.clf.fit(self.X_train, self.y_train)
                r.append(
                    self.clf.score(self.X_test, self.y_test)
                )
            res[wei if not isfunction(wei) else wei.__name__] = sum(r) / len(r)
        print(res)

    def k_fold(self):
        res = []
        k_range = range(100, 120)
        fold = 10
        for k in k_range:
            self.clf = KNeighborsClassifier(n_neighbors=k, weights='uniform', metric='euclidean')
            # 10次10折交叉验证
            ress = []
            for i in range(10):
                ress.append(
                    sum(cross_val_score(self.clf, self.X, self.y, cv=fold))/fold
                )
            res.append(
                sum(ress)/len(ress)
            )
            # print('n = %s, variance = %.2f' % (k, res[-1]))

    def predict(self):
        self.clf.predict(self.X_test)
        print("The Explained Variance: %.4f" % self.clf.score(self.X_test, self.y_test))

    def svm(self):
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

    def tree(self, max_depth=None, min_samples_leaf=1):
        # Create tree objectfor classification, here you can change the 
        # algorithm as gini or entropy (information gain) by default it is gini
        clf = tree.DecisionTreeClassifier(criterion='entropy', max_depth=max_depth, min_samples_leaf=min_samples_leaf)
        clf.fit(self.X_train, self.y_train)
        # predict value
        prediction = clf.predict(self.X_test)
        # predict accuracy
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))  
        dot_data = tree.export_graphviz(clf, out_file=None,
                                        feature_names=self.features,
                                        class_names=['no rain', 'rain'],
                                        filled = True, rounded = True,
                                        special_characters = True)
        graph = graphviz.Source(dot_data)
        graph.render('tree_min_samples_leaf{}_max_depth{}'.format(min_samples_leaf, max_depth))

def draw_sigmoid():
    z = np.linspace(-5, 5, 1000)
    g = 1 / (1 + np.exp(-z))
    plt.plot(z, g)
    plt.grid(True)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_position(('data', 0))
    ax.spines['left'].set_position(('data', 0))
    ax.set_xlabel('z')
    ax.set_ylabel('g', rotation='horizontal')
    plt.show()

def compare_models(X, y):
    """ 比较模型
    使用相同的数据集进行模型训练和预测，比较测试精度
    """
    n = 100
    res = {'logistic':[], 'knn':[], 'tree': []}
    for i in range(n):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=12)
        clf = LogisticRegression()
        clf.fit(X_train, y_train)
        res['logistic'].append(clf.score(X_test, y_test))
        clf = KNeighborsClassifier(n_neighbors=15, weights='uniform', metric='euclidean')
        clf.fit(X_train, y_train)
        res['knn'].append(clf.score(X_test, y_test))
        clf = tree.DecisionTreeClassifier()
        clf.fit(X_train, y_train)
        res['tree'].append(clf.score(X_test, y_test))
    res['logistic'] = sum(res['logistic'])/len(res['logistic'])
    res['knn'] = sum(res['knn'])/len(res['knn'])
    res['tree'] = sum(res['tree'])/len(res['tree'])
    return res

def export_model(clf, name):
    """ 导出模型，序列化模型 """
    # 保存成python支持的文件格式pickle, 在当前目录下可以看到
    with open(name, 'wb') as fw:
        pickle.dump(clf, fw)

def do_compare_models():
    # 比较模型
    # wd = WeatherData()
    res = compare_models(wd.X, wd.y)
    print(res)

def do_export_model():
    # 最优模型是knn分类器，模型参数如下
    clf = KNeighborsClassifier(n_neighbors=15, weights='uniform', metric='euclidean')
    # 训练模型
    wd = WeatherData()
    clf.fit(wd.X, wd.y)
    # 导出模型，用于在RPi Zero中导入
    export_model(clf, 'knn.pickle')

def test_model_import():
    # 测试导出的模型再导入是否正确
    with open('knn.pickle', 'rb') as fr:
        clf = pickle.load(fr)
        wd = WeatherData()
        res = clf.score(wd.X, wd.y)
        print('import model, score: ', res)

if __name__ == '__main__':
    # do_compare_models()
    do_export_model()
    # test_model_import()
    pass