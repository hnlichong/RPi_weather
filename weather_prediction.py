#! /usr/bin/env python3
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn import tree
import graphviz 
from weather_data import WeatherData

class Prediction(object):
    def __init__(self, dataset):
        self.X_train, self.X_test, self.y_train, self.y_test = dataset

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
        n_neighbors = 15
        # weights = 'uniform'
        weights = 'distance'
        # we create an instance of Neighbours Classifier and fit the data.
        clf = KNeighborsClassifier(n_neighbors, weights=weights)
        clf.fit(self.X_train, self.y_train)
        prediction = clf.predict(self.X_test)
        print("The Explained Variance: %.4f" % clf.score(self.X_test, self.y_test))  


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
    dataset = WeatherData().get_dataset()
    pred = Prediction(dataset)
    pred.svm()