'''
Created on 6 Jun 2013
Specs : Search images in the database by using the convension of word histograms
@author: Yrol Fernando
'''
import pickle
import sqlite3
import math
import numpy
import re
from PIL import Image
import matplotlib.pyplot as plt

class ImageSearch(object):
    
    #constructor
    def __init__(self,db,voc, inputImage):
        """ Initialise with the name of the database. Open connection upon creating the object and delete upon destroying"""
        self.con = sqlite3.connect(db)
        self.voc = voc
        self.inputImage = inputImage
        
    def __del__(self):
        self.con.close()
        
    #the following two methods will get the set of candidates that are suitable to compare
    def candidates_from_word(self,imword):
        """ Get list of images containing imword. """
        im_ids = self.con.execute("select distinct imid from imwords where wordid=%d" % imword).fetchall()
        return [i[0] for i in im_ids]
    
    def candidates_from_histogram(self,imwords):
        """ Get list of images with similar words. """
        
        # get the word ids
        words = imwords.nonzero()[0]
        
        # find candidates
        candidates = []
        
        for word in words:
            c = self.candidates_from_word(word)
            candidates+=c
        
        # take all unique words and reverse sort on occurrence
        tmp = [(w,candidates.count(w)) for w in set(candidates)]
        tmp.sort(cmp=lambda x,y:cmp(x[1],y[1]))
        tmp.reverse()
        
        # return sorted list, best matches first
        return [w[0] for w in tmp]
    
    #querying with an image ( following two methods)
    def get_imhistogram(self,imname):
        """ Return the word histogram for an image. """
        im_id = self.con.execute( "select rowid from imlist where filename='%s'" % imname).fetchone()
        s = self.con.execute("select histogram from imhistograms where rowid='%d'" % im_id).fetchone()
        
        # use pickle to decode NumPy arrays from string
        return pickle.loads(str(s[0]))
    
    #get the image by using regular expressions
    def getImageName(self, imageName):
		matches = re.findall(r"\'(.+?)\'",imageName)
		return ",".join(matches)
		
    
    #combining everything into one query
    def query(self,imname):
        """ Find a list of matching images for imname"""
        h = self.get_imhistogram(imname)
        candidates = self.candidates_from_histogram(h)
        matchscores = []
        
        for counter,imid in enumerate(candidates):
			
			if counter != 0:# prevent matchin the input image to its own
				cand_name = self.con.execute("select filename from imlist where rowid=%d" % imid).fetchone()
				cand_h = self.get_imhistogram(cand_name)
				cand_dist = math.sqrt( sum( (h-cand_h)**2 ) ) #use L2 distance 
				imageName = self.getImageName(str(cand_name))
				matchscores.append( (cand_dist,imid, imageName) )
            
        # return a sorted list of distances and database ids
        matchscores.sort()
        return matchscores
    
    #Computing the number of correct images
    def compute_ukbench_score(self,src,imlist):
        """ Returns the average number of correct
        images on the top four results of queries."""
        nbr_images = len(imlist)
        pos = numpy.zeros((nbr_images,4))
        
        # get first four results for each image
        for i in range(nbr_images):
            pos[i] = [w[1]-1 for w in src.query(imlist[i])[:4]]
            
        # compute score and return average
        score = numpy.array([ (pos[i]//4)==(i//4) for i in range(nbr_images)])*1.0
        return sum(score) / (nbr_images)
    
    def get_filename(self,imid):
        """ Return the filename for an image id"""
        s = self.con.execute( "select filename from imlist where rowid='%d'" % imid).fetchone()
        return s[0]
    
    #plotting the image
    def plot_results(self,src,res):
        """ Show images in result list 'res'."""
        plt.figure()
        nbr_results = len(res)
        
        for i in range(nbr_results):
            imname = src.get_filename(res[i])
            
            if imname == self.inputImage:
				continue
            else:
				plt.subplot(1,nbr_results,i+1)
				
				plt.imshow(numpy.array(Image.open('training_images/' + imname)))
				plt.axis('off')
				
        plt.show()

