import scipy as sp
import sklearn.cluster as sklCluster
import sklearn.manifold as sklManifold
import numpy as np


def do_visualization(self):
    distances = np.loadtxt("distances.txt")  # [:50,:50]
    gamma = 0.1

    similitudes = np.exp((-gamma * distances ** 2) / distances.std())

    nodes = [x for x in range(0, len(similitudes))]

    clusters = sklCluster.AffinityPropagation(affinity='precomputed', max_iter=100, verbose=True).fit(
        similitudes).labels_
    se = sklManifold.MDS(2, dissimilarity='precomputed', random_state=0).fit_transform(distances)

    edges = []
    treshold = 0.95
    for k in range(len(similitudes[0])):
        for j in range(len(similitudes[0])):
            if similitudes[k][j] >= treshold and k != j:
                edges.append((k, j))

    return nodes, clusters, edges