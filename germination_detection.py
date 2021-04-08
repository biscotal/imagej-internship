from ij import IJ, WindowManager, ImagePlus
from ij.measure import ResultsTable as rt
from ij.measure import Measurements
from math import *
import os
from loci.plugins.util import BFVirtualStack
from ij.gui import WaitForUserDialog, Toolbar
from ij.io import OpenDialog, SaveDialog
import csv
from javax.swing import JOptionPane

def openAnImageDialog(text):
	od = OpenDialog(text, None)  
	filename = od.getFileName()  
  
	if filename is None:  
  		print "User canceled the dialog!"  
	else:  
  		return od.getPath()

def saveAFileDialog():
   od = SaveDialog("Save the first results ...","results",".csv")  
   filename = od.getFileName()
   directory = od.getDirectory()
   filepath = directory + filename  
  
   if filename is None:  
      print "User canceled the dialog!"  
   else:  
      return filepath


# Stack or Image Sequence ?

myAnswer = ""
possibleAnswers = ["Image Sequence", "Stack (only one file)"]
while myAnswer == "":
  myAnswer = JOptionPane.showInputDialog(None, "Which type of image ?", \
  "Test", JOptionPane.QUESTION_MESSAGE, None, possibleAnswers, possibleAnswers[1])
if myAnswer == None:
  myAnswer = ""



# Beginning
if myAnswer == "Image Sequence":
	imageFilePath = openAnImageDialog("Select the first image of your Image Sequence.")
	IJ.run("Image Sequence...", "open={} sort use".format(imageFilePath))
if myAnswer == "Stack (only one file)":
	imageFilePath = openAnImageDialog("Select your stack.")
	imp1 = IJ.openImage(imageFilePath)
	imp1.show()
IJ.run("Split Channels")
WindowManager.getCurrentImage().close()
WindowManager.getCurrentImage().close()
imp = WindowManager.getCurrentImage()

# Asking user to set the threshold and get the size of objets that he wants to detect
IJ.run("Threshold...")
WaitForUserDialog("Threshold","Set a threshold slider avoiding maximum noise.\nThen click \'OK\'.").show()
IJ.run("Convert to Mask", "method=Default background=Dark black")
IJ.run("Set Measurements...", "area center display add redirect=None decimal=3")
imp.show()
IJ.run("Duplicate...", " ")
imp2 = WindowManager.getCurrentImage()
IJ.setTool(Toolbar.WAND)
WaitForUserDialog("Select an object","Click on one of the smallest objects that you want to detect.\nThen click \'OK\'.").show()
IJ.run("Measure")
minimumSizeOfObject = rt.getResultsTable().getValueAsDouble(0,0)/2
getrt = rt.getResultsTable()
rt.getResultsTable().reset()

# Beginning of the analyze
IJ.run("Select None")
IJ.run("Analyze Particles...", "size={}-Infinity display exclude".format(minimumSizeOfObject))
saveFirstResultsPath = saveAFileDialog()
saveLastResultsPath = saveFirstResultsPath[:-3] + "txt"
WaitForUserDialog("Information !","The analysis will start !\nResults will be saved at \"{}\".".format("..."+saveLastResultsPath[20:])).show()
IJ.saveAs("Results", saveFirstResultsPath)
imp2.close()

nbOfSeed = rt.getResultsTable().size() # I take the number of seeds detected
nbOfSlices = imp.getNSlices()

rt.getResultsTable().reset()

imp.show()

scale = imp.getCalibration()
xScale = scale.pixelWidth # x contains the pixel width in units
yScale = scale.pixelHeight # y contains the pixel height in units 

File = open(saveFirstResultsPath)

fichierCSV = csv.reader(File)
next(fichierCSV)

for line in fichierCSV:
   XM = float(line[3])/xScale
   YM = float(line[4])/yScale

   XM=int(XM)
   YM=int(YM)

   for i in range(1,imp.getNSlices()+1):
      imp.setSlice(i)
      IJ.doWand(XM, YM)
      IJ.run("Measure")

IJ.saveAs("Results", saveFirstResultsPath)      

File.close()

File_2 = open(saveFirstResultsPath)

fichierCSV_2 = csv.reader(File_2)
next(fichierCSV_2)

liste_area=[]
liste_X=[]
liste_Y=[]

for line in fichierCSV_2:
   #area = int(line[2])
   X = float(line[3])
   Y = float(line[4])
   #liste_area.append(area)
   liste_X.append(X)
   liste_Y.append(Y)

File_2.close()

startOfGermination=[]
Xposition=[]
Yposition=[]

for seedNb in range(0,nbOfSeed):
   sliceNb=seedNb*nbOfSlices 
   deltaR=0
   while deltaR < 1 and sliceNb<((seedNb+1)*nbOfSlices-1):
      Rprec=sqrt(liste_X[sliceNb]**2+liste_Y[sliceNb]**2)
      R=sqrt(liste_X[sliceNb+1]**2+liste_Y[sliceNb+1]**2)
      deltaR=abs(Rprec-R)
      sliceNb= sliceNb + 1
   startOfGermination.append(sliceNb-(seedNb*nbOfSlices)+1)
   Xposition.append(round(liste_X[sliceNb],3))
   Yposition.append(round(liste_Y[sliceNb],3))

with open(saveLastResultsPath,'w') as fic:
	fic.write('Time\tX\tY\n')
	for elt in range(0,nbOfSeed):
		fic.write(str(startOfGermination[elt])+'  ')
		fic.write(str(Xposition[elt])+'  ') 
		fic.write(str(Yposition[elt])+'\n')