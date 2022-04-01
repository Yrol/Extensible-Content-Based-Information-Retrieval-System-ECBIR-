'''
Created on 22 Jun 2013
Author: Yrol Fernando
Specs: Contains the logic of the image comparison mechanism
'''
#!/usr/bin/python
from UserOperations import UserOperations
import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web
from numpy import *
import random
import shutil
import os
import string
import pickle
import sqlite3

class CompareImages(UserOperations):

	#initialise the variables and calling the super class constructor
	def __init__(self,getImage):
		UserOperations.__init__(self)
		self.username = None
		self.dirCreated = None
		self.knowledgebase = os.getcwd() + '/knowledgebase' #folder which contains sift files
		self.imageFileDir = os.getcwd() + '/training_images' #folder contains images
		self.featlist = []
		self.imageList = []
		self.nbr_featurefiles = None
		self.runtimeError = 1
		self.vocabulary = None
		self.connection = None
		self.source = None
		self.inputImageName = getImage
		self.inputImageIndex = None 
		self.results = []

	#create a username randomly
	def createUsername(self):
		digits = "".join( [random.choice(string.digits) for i in xrange(8)] )
		chars = "".join( [random.choice(string.letters) for i in xrange(15)] )
		self.username = digits + chars

	#create a temporary folder using the random username created above	
	def createFolder(self, foldername):	
		while(self.dirCreated != True):
			if( os.path.exists(os.getcwd() + '/' + foldername)):
				continue
			else:
				foldername = self.username
				os.makedirs(os.getcwd() + '/' + foldername)
				self.dirCreated = True
		
		os.chmod(foldername, 0o777)
	
	#rename image to the random username created above and save it to temp directory
	def renameAndSaveImage(self, image):pass

	#generate sift file for the image
	def generateSiftFiles(self, imagename, username):
		self.processImage.generateSiftFiles(imagename, username)

	#get image file list
	def getImageFileList(self):
		try:
			self.imageList = os.listdir(self.imageFileDir)
			
			#append incoming input image to the list
			self.imageList.append('great-oak-stage-artists-impression.jpg')
			
			return self.imageList
		except:
			return self.runtimeError

	#get sift file list
	def getFeatureList(self):
		try:
			self.featlist = os.listdir(self.knowledgebase)
			
			return self.featlist 
		except:
			return self.runtimeError

	#create voabulary
	def createVocbulary(self):
		self.nbr_featurefiles = len(self.getFeatureList())
		self.featlist = [ self.knowledgebase + '/' + self.imageList[i][:-3]+'sift' for i in range(self.nbr_featurefiles) ]

		#append sift file of the incoming image
		self.featlist.append(self.username + '/' +  'great-oak-stage-artists-impression.sift')
		self.nbr_featurefiles += 1
		
		#calling vocabulary class through composition
		self.createVocabulary.__init__(self.username)
		self.createVocabulary.train(self.featlist,2500,10)
		
	def generateSiftFiles
		#saving vocabulary
		with open(self.username + '/' + self.username + '.pkl', 'wb') as f:
        		pickle.dump(self.createVocabulary,f)
   		print ('vocabulary is:', self.createVocabulary.name, self.createVocabulary.nbr_words)
   		
   		#loading vocabulary
   		with open(self.username + '/' + self.username + '.pkl', 'rb') as f:
			self.vocabulary = pickle.load(f)

	#function which reads features from sift files
	def readFeatures(self, filename):
		f = loadtxt(filename)
		return f[:,:4],f[:,4:]#feature locations, descriptors	

	#create database  for user and insert data
	def createDatabase(self):
		self.dbOperations.__init__(self.username + '/' + self.username + '.db', self.vocabulary)
		self.dbOperations.create_tables()
		
		#go through all images, project features on vocabulary and insert
		for i in range(self.nbr_featurefiles)[:100]:
			locs,descr = self.readFeatures(self.featlist[i])
			self.dbOperations.add_to_index(self.imageList[i],descr)
			
			#commit to database
			self.dbOperations.db_commit()
		

	#delete all the resources created at the end of the execution
	def deleteResorces(self):
		shutil.rmtree(self.username)
	
	#test number of features
	def getfts(self):
		return self.featlist
		
	#test number of images
	def getimgs(self):
		return self.imageList
		
	#this function do the comparison of images and return the distance and image (lower the distance closer the image)
	def compareImages(self):
		
		#get the index of the input image ( the index of the last image)
		self.inputImageIndex = (len(self.imageList)) - 1
		
		
		#retrun the 
		self.connection = sqlite3.connect(self.username + '/' + self.username + '.db')
		self.imageSerach.__init__(self.username + '/' + self.username + '.db', self.vocabulary, self.inputImageName)
		self.results = self.imageSerach.query(self.imageList[self.inputImageIndex ])[:10] #10 results 
		
		print(self.results)
		
		#from here we can get the results as we required


			
#unit testing
if __name__ == "__main__":
	print("start tornado service. the outline is same as the simple cv example")
	#can be call all of these operations within the tornado server function
	obj = CompareImages('great-oak-stage-artists-impression.jpg')
	obj.createUsername()
	obj.createFolder(obj.username)
	obj.generateSiftFiles('great-oak-stage-artists-impression.jpg', obj.username)
	obj.getImageFileList()
	obj.createVocbulary()
	obj.createDatabase()
	#obj.deleteResorces()
	print(len(obj.getfts()))
	print(len(obj.getimgs()))
	obj.compareImages()
	
	
