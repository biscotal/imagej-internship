from ij import IJ, WindowManager, ImagePlus
from ij.measure import ResultsTable as rt
from ij.measure import Measurements
from math import sqrt
import os
from loci.plugins.util import BFVirtualStack
from ij.gui import WaitForUserDialog, Toolbar
from ij.io import OpenDialog, SaveDialog
import csv
from javax.swing import JOptionPane
from java.awt import Font, Color
import time
from ij.gui import Roi, OvalRoi, Overlay, GenericDialog

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

def highlightSeeds(sliceNb,seedNb,Xposition,Yposition,imp):
	x = Xposition[seedNb]
	y = Yposition[seedNb]
	imp.setSlice(sliceNb)
	overlay = Overlay()
	roi = OvalRoi(x-50,y-50,100,100)
	roi.setStrokeColor(Color.green)
	roi.setStrokeWidth(10)
	imp.setRoi(roi)
	return roi

# Ask user for parameters
gui = GenericDialog("Which parameters do you want to measure ?")

gui.addMessage("Choose parameters that you want to measure, then click OK.\n(Area and Center of Mass are already checked)")
gui.addCheckbox("Perimeter", True)
gui.addCheckbox("Coordonates of bounding box", True)
gui.addCheckbox("Shape (Width and height)", True)

gui.showDialog() 

if gui.wasOKed():
   perimeter = gui.getNextBoolean()
   bounding = gui.getNextBoolean()
   shape = gui.getNextBoolean()

parameters = "area center"

if perimeter == True:
	parameters = parameters + " perimeter"
if bounding == True:
	parameters = parameters + " bounding"
if shape == True:
	parameters = parameters + " shape"


# Stack or Image Sequence ?

myAnswer = ""
possibleAnswers = ["Image Sequence", "Stack (only one file)"]
while myAnswer == "":
  myAnswer = JOptionPane.showInputDialog(None, "Which type of image ?", \
  "Choose", JOptionPane.QUESTION_MESSAGE, None, possibleAnswers, possibleAnswers[0])
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

# Do you want to crop the image ?
myAnswer = JOptionPane.showConfirmDialog(None, "Do you want to crop images ?")
if myAnswer == 0:
   IJ.setTool(Toolbar.RECTANGLE)
   WaitForUserDialog("What do you want to crop ?","Draw a rectangle.\nThen click \'OK\'.").show()
   IJ.run("Crop")         
    


IJ.run("Split Channels")
WindowManager.getCurrentImage().close()
WindowManager.getCurrentImage().close()
imp = WindowManager.getCurrentImage()

# Asking user to set the threshold and get the size of objets that he wants to detect
IJ.run("Threshold...")
WaitForUserDialog("Threshold","Set a threshold slider avoiding maximum noise.\nThen click \'OK\'.").show()
IJ.run("Convert to Mask", "method=Default background=Dark black")
IJ.run("Set Measurements...", "{} display add redirect=None decimal=3".format(parameters))
imp.show()
IJ.run("Duplicate...", " ")
imp2 = WindowManager.getCurrentImage()
IJ.run(imp2, "Options...", "iterations=1 count=1 black do=Nothing")
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

rt.getResultsTable().reset()

File.close()

#Time calibration

listeTemps = ['18/09/12 15:24']
date = listeTemps[0][:8]
jour = date[6:]
heure = listeTemps[0][9:][:2]
minutes = listeTemps[0][-3:]
heure = int(heure)
jour = int(jour)
for i in range(1,116):
    if heure<23:
        heure = heure + 1
    else:
        heure = 0
        jour = jour + 1
    date = date[:6]+str(jour)+' '+str(heure)+minutes
    listeTemps.append(date)

File_2 = open(saveFirstResultsPath)

fichierCSV_2 = csv.reader(File_2)
next(fichierCSV_2)

liste_X=[]
liste_Y=[]

for line in fichierCSV_2:
   X = float(line[3])
   Y = float(line[4])
   liste_X.append(X)
   liste_Y.append(Y)

File_2.close()

startOfGermination=[]
Xposition=[]
Yposition=[]
#listeDeltaR=[]

for seedNb in range(0,nbOfSeed):
   sliceNb=seedNb*nbOfSlices 
   deltaR=0
   while deltaR < 1 and sliceNb<((seedNb+1)*nbOfSlices-1):
      Rprec=sqrt(liste_X[sliceNb]**2+liste_Y[sliceNb]**2)
      R=sqrt(liste_X[sliceNb+1]**2+liste_Y[sliceNb+1]**2)
      deltaR=abs(Rprec-R)
      sliceNb= sliceNb + 1
   #listeDeltaR.append(deltaR)
   startOfGermination.append(sliceNb-(seedNb*nbOfSlices)+1)
   Xposition.append(round(liste_X[sliceNb],3))
   Yposition.append(round(liste_Y[sliceNb],3))

with open(saveLastResultsPath,'w') as fic:
	fic.write('\tTime\tX\tY\n')
	for elt in range(0,nbOfSeed):
		fic.write(str(listeTemps[startOfGermination[elt]-1])+'  ')
		fic.write(str(Xposition[elt])+'  ') 
		fic.write(str(Yposition[elt])+'\n')

# Highlight seeds
imp.show()
IJ.run("Select None")

listeSeedNb = []
for sliceNb in range(1,nbOfSlices+1):
	#listeSeedNb = []
	#listeSeedNb[:] = []
	for seedNb in range(0,nbOfSeed):
		if startOfGermination[seedNb] == sliceNb:
			listeSeedNb.append(seedNb)
	if listeSeedNb != None:
		overlay = Overlay()
		for i in range(0,len(listeSeedNb)):
			roi = highlightSeeds(sliceNb,listeSeedNb[i],Xposition,Yposition,imp)
			overlay.add(roi)
		imp.setOverlay(overlay)
		time.sleep(1)  