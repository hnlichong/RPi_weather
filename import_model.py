import pickle


def import_model():
    with open('knn.pickle', 'rb') as fr:
        clf = pickle.load(fr)
        res = clf.predict([22.2, 92.2, 1000.1])
        import pdb; pdb.set_trace()
        print('import model, predict res:  ', res)
