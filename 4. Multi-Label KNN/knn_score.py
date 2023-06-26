import pandas as pd
import numpy as np
from skmultilearn.adapt import MLkNN
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)

'''
Predictions are evaluated by ranking, employing the Leave One Out method. 
At each iteration the probability values obtained in the y_pred vector are sorted, 
keeping track of the initial indices representing the various domains, 
creating for each probability a tuple (<index>, <probability>)

The variables first and last passed as arguments to the KNN_score() function are used as follows.
The indices of the sectors in y_pred for the iterated positions in the first-last range (inclusive) are fetched, 
and if the indices stored as true labels for y_test are present among the sectors in this range, 
the score value referring to each position for the considered sector is incremented.
'''

def KNN_score(X, y, k, first, last):
    scores = {}
    labels = list(y.columns)
    for label in labels:
        scores[label] = {}
        for i in range(first,last+1):
            scores[label][i] = 0
            
    model = MLkNN(k = k)
    for i,_ in X.iterrows():
        X_train = X.drop(i, axis = 0).to_numpy()
        X_test = X.iloc[i].to_numpy().reshape(1,-1)
        y_train = y.drop(i, axis = 0).to_numpy()
        y_test = y.iloc[i].to_numpy()
        model.fit(X_train, y_train)
        y_pred = model.predict_proba(X_test).toarray()
        # Ordering predictions keeping trace of label indeces
        y_pred = [(p,y_pred[0][p]) for p in range(len(y_pred[0]))]
        y_pred = sorted(y_pred, key=lambda tup: tup[1], reverse=True)
        # Retrieving true labels indeces
        true_labels = [i for i in range(len(y_test)) if y_test[i] == 1]
        for j in true_labels:
            lab = labels[j]
            for r in range(first,last+1):
                # Retrieving 'r' best labels indeces
                best = [y_pred[b][0] for b in range(r)]
                # If true index 'j' appears in best increment the score
                if j in best:
                    scores[lab][r] += 1

    for lab in scores.keys():
        tot = len(y[y[lab] == 1])
        for i in scores[lab].keys():
            val = scores[lab][i]
            scores[lab][i] = '{:.1%}'.format(val/tot)
            
    data = []
    for i in range(len(labels)):
        data.append([])
        for j in range(first,last+1):
            data[i].append(scores[labels[i]][j])
    scores_df = pd.DataFrame(data, columns = [f"Best {k}" for k in range(first,last+1)], index = labels)
    
    return scores_df
