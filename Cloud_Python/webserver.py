'''
Created on 22 Jun 2013
Author: Yrol Fernando
Specs: This class allows the mobile users to connect to the application, In additionot that it also process the images 
'''
#!/usr/bin/python
from UserOperations import UserOperations
import os, tempfile, shutil
from abc import ABCMeta, abstractmethod
import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web
from tornado.options import define, options #test
from numpy import *
import string
import random
import pickle
import sqlite3
import csv

define("port", default=8000, help="run on the given port", type=int)

dir_modified = "files/uploads/"
dir_original = "files/uploads/original/"

class CompareImages(UserOperations):
	
	#create a username randomly
	def createUsername(self):
		digits = "".join( [random.choice(string.digits) for i in xrange(8)] )
		chars = "".join( [random.choice(string.letters) for i in xrange(15)] )
		return digits + chars
		
	#create a folder name
	def createFolder(self, foldername):
			
		dirCreated = None
		
		while(dirCreated != True):
			if( os.path.exists(os.getcwd() + '/' + dir_modified + foldername)):
				continue
			else:
				os.makedirs(os.getcwd() + '/' + dir_modified + foldername)
				dirCreated = True
				
		#add permision to the folder
		os.chmod(os.getcwd() + '/' + dir_modified + foldername, 0o777)
		return foldername
	
	#generation sift files
	def generateSiftFiles(self, imagename, username):
		self.processImage.generateSiftFiles(imagename, username)
		
	#get image file list
	def getImageFileList(self, inputImage):
		imageList = []
		imageFileDir = os.getcwd() + '/training_images'
		try:
			imageList = os.listdir(imageFileDir)
			#append incoming input image to the list
			imageList.append(inputImage)
			return imageList
		except:
			return "An error occured"
			
	def getFeatureList(self):
		knowledgebase = os.getcwd() + '/knowledgebase'
		featlist = []
		
		try:
			featlist = os.listdir(knowledgebase)
			return featlist 
		except:
			return "An error occured"
	
	#create and save vocabulary
	def createVocbulary(self, getImageList, getFeatureList, siftFile, username):
		
		knowledgebase = '/knowledgebase'
		
		nbr_featurefiles = len(getFeatureList)
		featlist = [ os.getcwd() + '/' + knowledgebase + '/' + getImageList[i][:-3]+'sift' for i in range(nbr_featurefiles) ]
		
		#append sift file of the incoming image
		featlist.append(siftFile)
		nbr_featurefiles += 1
		
		#calling vocabulary class through composition
		self.createVocabulary.__init__(username)
		self.createVocabulary.train(featlist,2500,10)
		
		#saving vocabulary
		path = os.getcwd() + '/files/uploads/' + username
		
		with open(path + '/' + username + '.pkl', 'wb') as f:
        		pickle.dump(self.createVocabulary,f)
   		print ('vocabulary is:', self.createVocabulary.name, self.createVocabulary.nbr_words)
	
	#function which reads features from sift files
	def readFeatures(self, filename):
		f = loadtxt(filename)
		return f[:,:4],f[:,4:] # feature locations, descriptors	
	
	#creating the database
	def createDatabase(self, username, vocabulary, getFeatureList, getImageList, siftFile, getInputImage):
		
		nbr_featurefiles = len(getFeatureList)
		featlist = ['knowledgebase/' + getImageList[i][:-3]+'sift' for i in range(nbr_featurefiles) ]
		
		#append sift file of the incoming image
		featlist.append(siftFile)
		nbr_featurefiles += 1
		
		path = os.getcwd() + '/files/uploads/' + username
		
		self.dbOperations.__init__(path + '/' + username + '.db', vocabulary)
		self.dbOperations.create_tables()
		
		#go through all images, project features on vocabulary and insert
		for i in range(nbr_featurefiles)[:100]:
			locs,descr = self.readFeatures(featlist[i])
			self.dbOperations.add_to_index(getImageList[i],descr)
			
			#commit to database
			self.dbOperations.db_commit()
			
	#load vocabulary
   	def loadVocabulary(self, username):
		path = os.getcwd() + '/files/uploads/' + username
		with open(path + '/' + username + '.pkl', 'rb') as f:
			vocabulary = pickle.load(f)
			return vocabulary
	
	#compare images
	def compareImages(self, username, getVocabulary, getImageList, inputImageName):
		
		#get the index of the input image ( the index of the last image)
		inputImageIndex = (len(getImageList)) - 1
		
		#retrun the 
		path = os.getcwd() + '/files/uploads/' + username
		connection = sqlite3.connect(path + '/' + username + '.db')
		self.imageSerach.__init__(path + '/' + username + '.db', getVocabulary, inputImageName)
		results = self.imageSerach.query(getImageList[inputImageIndex ])[:3] #10 results 
		
		#print(results)
		
		return results
	
	#create a csv file
	def createCSVFile(self, result, fileName):
		print fileName
		path = os.getcwd() + '/files/uploads/' + fileName
		with open(path + "/" + fileName + '.txt', "wb") as f:
			writer = csv.writer(f)
			writer.writerows(result)
                         
############################### Tornado web server starts here #################################
class Application(tornado.web.Application):
	
    def __init__(self):
        handlers = [ (r"/", HomeHandler), (r"/upload", UploadHandler),
                     (r"/uploads/(.*)", tornado.web.StaticFileHandler,
                        {"path": os.path.join(os.path.dirname(__file__), dir_modified)}), 
                     (r"/process", ProcessHandler) ]
        print 'Server listning...\n'

        if not os.path.exists(dir_original):
            os.makedirs(dir_original)
        if not os.path.exists(dir_modified):
            os.makedirs(dir_modified)

        tornado.web.Application.__init__(self, handlers)

class HomeHandler(tornado.web.RequestHandler):

    def get(self):

        self.finish('Upload File: ');

class UploadHandler(tornado.web.RequestHandler):

    def post(self):
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        tmp_name = tmp_file.name.split("/")[-1]
        output_file = open(dir_original + tmp_name, 'w')

        image = self.request.files['data'][0]
        output_file.write(image['body'])

        image_path = os.getcwd() + dir_original + tmp_name
		
		#localhost address 10.0.2.2, actual mechine address : 192.168.1.68
        img_URL = "http://192.168.1.68:8000/uploads/original/%s" % tmp_name
        #img_URL = "http://mobiletest.simplecv.org:8000/uploads/original/%s" % tmp_name

        print image_path
        self.finish(img_URL)

class ProcessHandler(tornado.web.RequestHandler):

    def post(self):
        given_path = self.request.arguments['picture'][0] #linkToOriginal - picture (in the android application)
        
        #create an object of the compare images (the class above in the same file)
        obj = CompareImages()
        
        #creating a temp folder
        temp_folder = obj.createFolder(obj.createUsername())
        
        image_name = given_path.split('/')[-1]
        original_path = dir_original + image_name
        modified_path = dir_modified + temp_folder + '/' + image_name

		#copy image to the user directory
        shutil.copyfile(original_path, modified_path);     
       
        #generate sift file
        obj.generateSiftFiles(modified_path, temp_folder)
        
        #image list
        imageList = obj.getImageFileList(modified_path)
        
        #features list (sift files)
        featureList = obj.getFeatureList()
        
        #sift file
        siftFileGenerated = os.path.splitext(modified_path)[0] + ".sift" 
        
        #create vocabulary
        obj.createVocbulary(imageList, featureList, siftFileGenerated, temp_folder)
        
        #load vocabulary
        vocabulary = obj.loadVocabulary(temp_folder)
        
        #create database
        obj.createDatabase(temp_folder, vocabulary, featureList, imageList, siftFileGenerated, modified_path)
        
        #compare the image 
        results = obj.compareImages(temp_folder, vocabulary, imageList, modified_path)
        
        #create the CSV file
        obj.createCSVFile(results, temp_folder)
        
 
		#URL of the end result - localhost address 10.0.2.2, actual mechine address : 192.168.1.68
        img_URL = "http://192.168.1.68:8000/uploads/"  + temp_folder + "/" + "%s" % image_name
        txt_file = temp_folder + ".txt"
        txt_URL = 	"http://192.168.1.68:8000/uploads/"  + temp_folder + "/" + "%s" % txt_file 
    
        #return the URL of the result to the application
        self.finish(txt_URL)
		
if __name__ == "__main__":

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()
    


