# imagej-internship

This ImageJ macro/plugin can be used to detect the begining of germination of seeds.
It's based on a shifting dectection : center of mass position of each seed is detected on every slice, and then 
the absolute difference of positions between 2 slices is calculated. At a given threshold (deltaR > 1 by default),
seeds are considered to be germinating.
