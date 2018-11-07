#! /usr/bin/env python3
import pickle

def import_model():
    with open('knn.pickle', 'rb') as fr:
        clf = pickle.load(fr)
        res = clf.predict([22.2, 92.2, 1000.1])
        print('import model, predict res:  ', res)

if __name__ == '__main__':
    import_model()
