'''
Created on 5 Jun 2013
Spec : This is the abtract class that generalises both client and administrator operations
@author: Yrol Fernando
'''
#!/usr/bin/python
from ProcessImages import ProcessImages
from DBOperations import DBOperations
from abc import ABCMeta, abstractmethod

class Operations(object):

	__metaclass__ = ABCMeta	

	def __init__(self):
		self.processImage = ProcessImages();
		self.dbOperations = DBOperations("NULL", "NULL")

	#Declaring the abstract classes
	@abstractmethod
	def generateSiftFiles(self, imagename, username):pass

	@abstractmethod
	def createFolder(self,foldername):pass

	@abstractmethod
	def createDatabase(self):pass

'''
#unit testing
if __name__ == "__main__":
	obj = Operations()
	obj.generateSiftFiles();
'''

