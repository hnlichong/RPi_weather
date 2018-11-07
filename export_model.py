#! /usr/bin/env python3
import pickle

from sklearn.neighbors import KNeighborsClassifier

from weather_data import WeatherData


def do_export_model():
    # 最优模型是knn分类器，模型参数如下
    clf = KNeighborsClassifier(n_neighbors=15, weights='uniform', metric='euclidean')
    # 训练模型
    wd = WeatherData()
    clf.fit(wd.X, wd.y)
    # 导出模型，用于在RPi Zero中导入
    export_model(clf, 'knn.pickle')

def export_model(clf, name):
    """ 导出模型，序列化模型 """
    # 保存成python支持的文件格式pickle, 在当前目录下可以看到
    with open(name, 'wb') as fw:
        pickle.dump(clf, fw)


if __name__ == '__main__':
    do_export_model()
