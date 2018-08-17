#! /usr/bin/env python3
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn import tree
import graphviz 
from weather_data import WeatherData
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split

class Prediction(object):
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=12)


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

    def tree(self):
        # Create tree objectfor classification, here you can change the 
        # algorithm as gini or entropy (information gain) by default it is gini
        clf = tree.DecisionTreeClassifier(criterion='gini')
        clf.fit(self.X_train, self.y_train)
        # predict value
        prediction = clf.predict(self.X_test)
        # predict accuracy
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))  
        # dot_data = tree.export_graphviz(clf, out_file=None) 
        # graph = graphviz.Source(dot_data) 
        # graph.render("weather") 


if __name__ == '__main__':
    wd = WeatherData()
    pred = Prediction(
        X=wd.X, y=wd.y)
    pred.knn_k()
