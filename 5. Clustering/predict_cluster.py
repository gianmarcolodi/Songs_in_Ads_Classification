import pandas as pd
import numpy as np
import math
from sklearn.cluster import AgglomerativeClustering
from spotify import SpotifyAPI

'''
Trying to divide the song samples into clusters that include songs that are similar to each other, 
and then analyze the sectors to which they belong, visualizing for each cluster what the most recurring sectors are.

Then, given a song outside the dataset, assigning it to the closer cluster and display the most common sector in that cluster, as a prediction.
'''

feat_df = pd.read_csv("2. Labeling/features_2.csv")
max_tempo = feat_df["tempo"].max()
min_tempo = feat_df["tempo"].min()
feat_df["tempo"] = (feat_df["tempo"] - min_tempo)/(max_tempo - min_tempo)

feat_mood = feat_df.filter(["danceability","energy","valence","tempo"]).to_numpy()
sectors_df = pd.read_csv("sectors_2.csv")
sectors = sectors_df.columns

ac = AgglomerativeClustering(n_clusters = 4)
sectors_df["Cluster"] = ac.fit_predict(feat_mood)

# Songs percentage of a certain sector for each cluster
sect_count = []
for i in range(4):
    sect_count.append([])
    clust = sectors_df[sectors_df["Cluster"]==i]
    for sec in sectors:
        tot = len(sectors_df[sectors_df[sec] == 1])
        n = len(clust[clust[sec] == 1])
        sect_count[i].append("{:.1%}".format(n/tot))

cluster_df = pd.DataFrame(sect_count, columns = sectors, index = [f"Cluster {i}" for i in range(4)])

spo = SpotifyAPI(client_id, client_secret)

def euc_dist(v1, v2):
    sum_sqr_dif = 0
    for i in range(len(v1)):
        sum_sqr_dif += (v1[i] - v2[i])**2
    return math.sqrt(sum_sqr_dif)

def sectors_proba(id_):
    res = spo.get_features(id_)["audio_features"][0]
    features = np.array([res["danceability"],res["energy"],res["valence"],res["tempo"]])
    features[3] = (features[3]-min_tempo)/(max_tempo-min_tempo)
    
    min_dist = (100,0)
    for i in range(len(feat_mood)):
        sample = feat_mood[i]
        dist = euc_dist(sample, features)
        if dist < min_dist[0]:
            min_dist = (dist,i)
            
    cluster_pred = sectors_df.iloc[min_dist[1]][-1]
    proba = cluster_df.iloc[cluster_pred]
    proba = [[sectors[i], float(proba[i][:-1])] for i in range(len(proba))]
    proba.sort(key = lambda prob: prob[1], reverse = True)
    for p in proba:
        p[1] = str(p[1])+'%'
    
    print("Predicted Cluster: " + str(cluster_pred))
    return proba
