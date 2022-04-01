'''
Created on 22 Jun 2013
Author: Yrol Fernando
Specs: The abstract class that generalise the user operations
'''
#!/usr/bin/python
from Operations import Operations
from CreateVocabulary import CreateVocabulary
from ImageSearch import ImageSearch
from abc import ABCMeta, abstractmethod

class UserOperations(Operations):
	
	__metaclass__ = ABCMeta	

	#Access the superclass as well as adding composition within the constructor
	def __init__(self):
		Operations.__init__(self)
		self.createVocabulary = CreateVocabulary()
		self.imageSerach = ImageSearch("NULL","NULL", "NULL")

	#Declaring the abstract classes
	@abstractmethod
	def generateSiftFiles(self, imagename, username):pass

	@abstractmethod
	def createFolder(self,foldername):pass

	@abstractmethod
	def createVocbulary(self):pass

	@abstractmethod
	def createDatabase(self):pass
	
	
