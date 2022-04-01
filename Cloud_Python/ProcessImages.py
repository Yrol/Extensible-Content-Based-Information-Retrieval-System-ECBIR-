'''
Created on 22 Jun 2013
Author: Yrol Fernando
Specs: Process the images such as generating the SIFT files. The output of this code is to generate SIFT files
'''
#!/usr/bin/python
import os
from PIL import Image
from numpy import *
import pylab

class ProcessImages(object):

	#process image and generate the .sift file
	def generateSiftFiles(self, image, username, params="--edge-thresh 10 --peak-thresh 5"):

		 #Split image name and extension
    		imagename = os.path.splitext(os.path.basename(image))[0]
    		imageextension = os.path.splitext(os.path.basename(image))[1] 

		#convert to pgm file
		if imageextension != '.pgm':
			im = Image.open(image).convert('L')
			im.save( 'files/uploads/' + username + '/' +username + '.pgm')
		else:
			im = Image.open(image)
			im.save( 'files/uploads/' + username + '/' + username + '.pgm')
		
		path = os.getcwd() + '/files/uploads/' + username

		cmmd = str("sift_library/./sift " + path +"/"  + username + ".pgm" + " --output=" + path + "/" + imagename + ".sift" + " "+params)

		os.system(cmmd)
		print('processed', imagename, 'to', imagename, '.sift')

'''
#unit testing
if __name__ == "__main__":
	obj = ProcessImages()
	obj.generateSiftFiles('great-oak-stage-artists-impression.jpg', 'test')
'''

