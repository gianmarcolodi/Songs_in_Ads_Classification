from spotify import SpotifyAPI
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")
client_id = "c060ec48cdb841be989e77801cec08ef"
client_secret = "dfea5bbf85134f97937397e7802ba491"
spo = SpotifyAPI(client_id, client_secret)

features = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
data = {}
for f in features:
    data[f] = []

IDs = list(df["ID"])
cuts = [i*100 for i in range(1,len(IDs)//100 +1)]
IDs = np.split(IDs, cuts)
for idx in IDs:
    idx = idx.tolist()
    feats = spo.get_features(idx)["audio_features"]
    for f in features:
        for feat in feats:
            data[f].append(feat[f])

df_feat = pd.DataFrame(data, columns = features)
df = pd.concat([df, df_feat], axis = 1)
df.to_csv("features.csv", index = False)  
            
