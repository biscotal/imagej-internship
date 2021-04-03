import csv
from ij import IJ, WindowManager, ImagePlus
from ij.measure import ResultsTable as rt
from ij.measure import Measurements
from math import *

IJ.run("Image Sequence...", "open=C:/Users/Valen/Documents/Stage/18_09_12_Cowpea_IRD_2P1_01_B2_zz/Cowpea_____1809121524_2P1_000.tiff sort use")
IJ.run("Split Channels")
WindowManager.getImage("18_09_12_Cowpea_IRD_2P1_01_B2_zz (blue)").close()
WindowManager.getImage("18_09_12_Cowpea_IRD_2P1_01_B2_zz (green)").close()
imp = WindowManager.getImage("18_09_12_Cowpea_IRD_2P1_01_B2_zz (red)")
IJ.run("Threshold...")
IJ.setThreshold(160, 255)
IJ.run("Convert to Mask", "method=Default background=Dark black")
IJ.run("Set Measurements...", "area center display add redirect=None decimal=3")
imp.show()
IJ.run("Duplicate...", " ")
imp2 = WindowManager.getCurrentImage()
IJ.run("Analyze Particles...", "size=10-Infinity display exclude")
IJ.saveAs("Results", "C:/Users/Valen/Documents/Stage/Semaine 1/particles_analysis.csv")
imp2.close()

nbOfSeed = rt.getResultsTable().size()-1 # I take the number of seeds detected
nbOfSlices = imp.getNSlices()

rt.getResultsTable().reset()

#nbOfSeed=int(nbOfSeed)
#nbOfSlices=int(nbOfSlices)

imp.show()

stack = imp.getStack()

File = open('C:/Users/Valen/Documents/Stage/Semaine 1/particles_analysis.csv')

fichierCSV = csv.reader(File)
next(fichierCSV)

for line in fichierCSV:
   XM = float(line[3])
   YM = float(line[4])

   XM=int(XM)
   YM=int(YM)

   for i in range(1,imp.getNSlices()+1):
      imp.setSlice(i)
      IJ.doWand(XM, YM)
      IJ.run("Measure");

IJ.saveAs("Results", "C:/Users/Valen/Documents/Stage/Semaine 1/particles_analysis_for_MATLAB.csv")      

File.close()

File_2 = open('C:/Users/Valen/Documents/Stage/Semaine 1/particles_analysis_for_MATLAB.csv')

fichierCSV_2 = csv.reader(File_2)
next(fichierCSV_2)

liste_area=[]
liste_X=[]
liste_Y=[]

for line in fichierCSV_2:
   area = int(line[2])
   X = float(line[3])
   Y = float(line[4])
   liste_area.append(area)
   liste_X.append(X)
   liste_Y.append(Y)

File_2.close()

startOfGermination=[]
Xposition=[]
Yposition=[]

for seedNb in range(0,nbOfSeed):
   sliceNb=seedNb*nbOfSlices 
   deltaR=0
   while deltaR < 3 and sliceNb<(len(liste_X)-1):
      Rprec=sqrt(liste_X[sliceNb]**2+liste_Y[sliceNb]**2)
      R=sqrt(liste_X[sliceNb+1]**2+liste_Y[sliceNb+1]**2)
      deltaR=abs(Rprec-R)
      sliceNb= sliceNb + 1
   startOfGermination.append(sliceNb-(seedNb*nbOfSlices))
   Xposition.append(round(liste_X[sliceNb],3))
   Yposition.append(round(liste_Y[sliceNb],3))

with open('C:/Users/Valen/Documents/Stage/Semaine 1/Begining_of_germination.txt','w') as fic:
	fic.write('Time\tX\tY\n')
	for elt in range(0,nbOfSeed):
		fic.write(str(startOfGermination[elt])+'  ')
		fic.write(str(Xposition[elt])+'  ') 
		fic.write(str(Yposition[elt])+'\n')