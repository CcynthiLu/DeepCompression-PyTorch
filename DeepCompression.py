import torch
import numpy as np
import torch.nn as nn
from sklearn import cluster


class DeepCompression(nn.Module):
    def __init__(self, threshold=0.02, k_means=16):
        self.threshold = threshold
        self.k_means   = k_means

    # returns the index of the closest centroid value
    def closest(input, centroids):
        idx = (np.abs(centroids-input)).argmin()
        return idx

    def prune(self, model):
        for param in model.parameters():
            param = torch.gt((torch.abs(param)),self.threshold).float() # need to add "absolute"
        return model

    def quantize(self, model):
        '''
            Quantization Process
        ___________________________
        1. Cluster matrix into centroids
        2. Create an index matrix
        3. Iterate over the input matrix, putting the closest centroid index into the index matrix

        '''
        model_ = []
        for param in model.parameters():

            # 1. Clustering.  Probably done better as linear intervals - since a pruned network
            # will cluster heavily around 0
            kmeans = cluster.KMeans(n_clusters=k_means, n_init=20).fit(param.reshape((-1,1)))

            # 2. Create codebook vector
            centroids = kmeans.cluster_centers_

            # 3. Create index matrix
            index_matrix = np.ndarray(param.shape)

            # 4. Fill index matrix : TODO make this more numpy
            vectorized_matrix = param.reshape(1,-1)[0]

            for i,value in enumerate(vectorized_matrix):
                vectorized_matrix[i] = closest(value, centroids)

            index_matrix = vectorized_matrix.reshape(param.shape)

            model_.append((param, centroids))

        # need to reconstruct PyTorch module

        return QuantizedNN(model_)

    '''
        May not do this. Helps compress network size but not really relevant
        to performance since I assume we decompress the model before running
        inferences
    '''
    def huffman_encode(self, model):
        return 0

    def compress(self, model):
        # Prune and retrain
        model = prune(model)
        model = retrain_pruned_model(model, num_epochs)

        # Quantize and retrain
        model_ = quantize(model)
        model_ = retrain_quantized_model(model, num_epochs)

        # Huffman encode weight matrix
        # model__ = huffman_encode(model_)
        
        return model_
