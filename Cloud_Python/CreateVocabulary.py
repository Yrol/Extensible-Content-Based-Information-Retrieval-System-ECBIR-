#!/usr/bin/python
from scipy.cluster.vq import *
import os
import math
from numpy import *

class CreateVocabulary(object):

	#constructor
	def __init__(self,name = None):
		self.name = name
		self.voc = []
		self.idf = []
		self.trainingdata = []
		self.nbr_words = 0

	#read features from files
	def readFeatures(self, filename):
		f = loadtxt(filename)
		return f[:,:4],f[:,4:] # feature locations, descriptors	

	def train(self,featurefiles,k=100,subsampling=10):

		nbr_images = len(featurefiles)

		# read the features from file
		descr = []
		descr.append(self.readFeatures(featurefiles[0])[1])
		descriptors = descr[0] #stack all features for k-means

		for i in arange(1,nbr_images):
		    descr.append(self.readFeatures(featurefiles[i])[1])
		    descriptors = vstack((descriptors,descr[i]))
		    
		# k-means: last number determines number of runs
		self.voc,distortion = kmeans(descriptors[::subsampling,:],k,1)
		self.nbr_words = self.voc.shape[0]

		# go through all training images and project on vocabulary
		imwords = zeros((nbr_images,self.nbr_words))

		for i in range( nbr_images ):
		    imwords[i] = self.project(descr[i])
		    
		nbr_occurences = sum( (imwords > 0)*1 ,axis=0)

		self.idf = log( (1.0*nbr_images) / (1.0*nbr_occurences+1) )
		self.trainingdata = featurefiles

	#will not be used within the project used only for experimantal puposes 
	def project(self,descriptors):
		""" Project descriptors on the vocabulary
		to create a histogram of words. """

		# histogram of image words
		imhist = zeros((self.nbr_words))
		words,distance = vq(descriptors,self.voc)

		for w in words:
		    imhist[w] += 1
		    
		return imhist

'''
#unit testing
if __name__ == "__main__": 
	knowledgebase = os.getcwd() + '/knowledgebase'
	featlist = "3481087259_b294b61784.sift"
	obj = CreateVocabulary('TestVoc')
'''

