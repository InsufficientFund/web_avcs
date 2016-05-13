import glob
import cv2
import numpy as np
from copy import deepcopy
from skimage import feature
import csv
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


class LocalBinaryPatterns:
    def __init__(self, numPoints, radius):
        # store the number of points and radius
        self.numPoints = numPoints
        self.radius = radius

    def describe(self, image, eps=1e-7):
        # compute the Local Binary Pattern representation
        # of the image, and then use the LBP representation
        # to build the histogram of patterns
        lbp = feature.local_binary_pattern(image, self.numPoints,
            self.radius, method="uniform")
        (hist, _) = np.histogram(lbp.ravel(),
            bins=np.arange(0, self.numPoints + 2),
            range=(0, self.numPoints + 1))

        # normalize the histogram
        hist = hist.astype("float")
        hist /= (hist.sum() + eps)

        # return the histogram of Local Binary Patterns
        return hist, lbp


class lbp_feature:
    def __init__(self):
        self.lbpClass = LocalBinaryPatterns(8, 1)
        self.list_range = [slice(0, 11), slice(11, 22), slice(22, 33),
                          slice(33, 44), slice(44, 54), slice(54, 64)]
        self.image = None
        self.feature_list = []

    def read_image(self, image):
        self.image = cv2.equalizeHist(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        self.feature_list = []

    def extract_feature(self, height, width, area, answer=None):
        hist_ratio = []
        hist_max = []
        for i in self.list_range:
            for j in self.list_range:
                compute_pic = self.image[i, j]
                hist, lbp = self.lbpClass.describe(compute_pic)
                histR = hist[0:5].sum()/hist[5:10].sum()
                if np.isinf(histR.max()):
                	hist_ratio.append(0.0)
                	hist_max.append(0.0)	
                else:
                	hist_ratio.append(round(histR, 6))
                	hist_max.append(round(hist.max(), 6))
        if answer == None:
            return np.hstack((hist_ratio, hist_max, height, width, area))
        else:
            return np.hstack((hist_ratio, hist_max, height, width, area, answer))