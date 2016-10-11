#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PIL import Image

from optparse import OptionParser

from svmutil import *

import os

import re

def ArgModule():

	Usage = '%prog -f PictureName -m ("t" or "r")'

	Arg = OptionParser(usage = Usage)

	Arg.add_option('-f',dest="filename",help="A image filename")

	Arg.add_option('-d',dest="dir",help="A directory which has all image")

	Arg.add_option('-a',dest="feature",help="According to the img to create a feature file")

	Arg.add_option('-m',dest="mode",help="T for tarinnig,R for verify")

	(options,args) = Arg.parse_args()

	if options.filename is None and options.dir is None and options.feature is None and options.mode is None:

		print "Must Input one argument."

		print "Please use '-h' to get help."

	if options.filename is not None and options.mode:			#@In this case you will get in to the mode you chose 

		return options.filename,options.mode		 			#trainnig the maching or verify the code; 

	if options.dir is not None:									#@In this case you can split some random picture to 

		getPath = []											#expand your verify-code database;

		name = []

		for parent,dirnames,dirnames in os.walk(options.dir):

			for dirname in dirnames:

				getPath.append(parent + dirname)

				name.append(dirname)

		return getPath,options.mode
	
	if options.feature is not None:								#@In this case you can translate lots of picture in 

		DealImg(options.feature)								#the directory which get name of 'Image/1,Image/2...'

		TrainSvmModel()											#to the string of the python-libsvm

		exit(0)

def GrayToBinary():

	table = []

	threshold = 128

	for i in range(256):

		if i < threshold:

			table.append(0)

		else:

			table.append(1)

	return table


def Denoise(img,x,y):						#@This function is to denoise the img,maybe some single point in the picture

	currentPix = img.getpixel((x,y))		#@It is hard to distinguish the code from the img with out this function

	if currentPix is 1:						

		return 0

	if y == 0:

		if x == 0:

			num = currentPix + img.getpixel((x+1,y)) + img.getpixel((x+1,y+1)) + img.getpixel((x,y+1))

			return 4-num

		elif x == img.width-1:

			num = currentPix + img.getpixel((x-1,y)) + img.getpixel((x,y+1)) + img.getpixel((x-1,y+1))

			return 4-num

		else:

			num = currentPix + img.getpixel((x-1,y)) + img.getpixel((x-1,y+1)) + img.getpixel((x,y+1)) + img.getpixel((x+1,y+1)) + img.getpixel((x+1,y))

			return 6-num

	elif y == img.height-1:

		if x == 0:

			num = currentPix + img.getpixel((x,y-1)) + img.getpixel((x+1,y)) + img.getpixel((x+1,y-1))

			return 4-num

		elif x == img.width-1:

			num = currentPix + img.getpixel((x-1,y)) + img.getpixel((x,y-1)) + img.getpixel((x-1,y-1))

			return 4-num

		else:

			num = currentPix + img.getpixel((x-1,y)) + img.getpixel((x-1,y-1)) + img.getpixel((x,y-1)) + img.getpixel((x+1,y-1)) + img.getpixel((x+1,y))
			
			return 6-num
	else:

		if x == 0:

			num = currentPix + img.getpixel((x,y-1)) + img.getpixel((x+1,y-1)) + img.getpixel((x+1,y)) + img.getpixel((x+1,y+1)) + img.getpixel((x,y+1))

			return (6-num)

		elif x == img.width-1:

			num = currentPix + img.getpixel((x,y-1)) + img.getpixel((x-1,y-1)) + img.getpixel((x-1,y)) + img.getpixel((x-1,y+1)) + img.getpixel((x,y+1))

			return 6-num

		else:

			num = currentPix + img.getpixel((x-1,y-1)) + img.getpixel((x,y-1)) + img.getpixel((x+1,y-1)) + img.getpixel((x+1,y)) + img.getpixel((x+1,y+1)) + img.getpixel((x,y+1)) + img.getpixel((x-1,y+1)) + img.getpixel((x-1,y))

			return 9-num




def ApiDenoise(img,path):								#@A function which is to operate "Denoise()" function

	xSize,ySize = img.size

	point = []

	for y in range(ySize):

		for x in range(xSize):
 
			num = Denoise(img,x,y)

			if num == 1:

				point.append((x,y))

	for a in point:

		x,y = a

		img.putpixel((x,y),1)							#@Denoise all single point in the picture we found

	for size in range(0,4):

		box = (size*10,0,(size+1)*10-4,10)

		singleImg = img.crop(box)

		name = ''

		string = re.findall(r'\/([0-9][a-zA-Z]*)\.',path)

		for i in string:

			name = name + i

		if  not os.path.exists('SingleImg/'):

			os.makedirs('SingleImg')

		singleImg.save('SingleImg/' + name + '-' + str(size) + '.jpg')	#@Save the splited picture and rename. 


def SingleDealImg(img,path,mode):					#@Verify function,including denoise,and split picture,two 

	xSize,ySize = img.size

	point = []

	for y in range(ySize):

		for x in range(xSize):
 
			num = Denoise(img,x,y)

			if num == 1:

				point.append((x,y))

	for a in point:

		x,y = a

		img.putpixel((x,y),1)

	if mode == 't':												#@If you choose trainning mode you should input the answer

		code = raw_input("Input the result of verify code:")	#@just like to tell the maching what is the '1' number like

	for size in range(0,4):										#@in the picture

		box = (size*10,0,(size+1)*10-4,10)

		singleImg = img.crop(box)

		name = ''

		string = re.findall(r'([0-9A-z]*)\.',path)

		for i in string:

			name = name + i

		singleFeature = GetFeature(singleImg)

		if mode == 't':											#@In the trainnig mode,the maching must know the number.

			result = code[int(size)]

		else:

			result = '0'										#@In the verify mode,the flag must be '0'.

		single = 0

		for line in singleFeature:

			single = single + 1

			result = result + ' ' + str(single) + ':' + str(line)

		filename = name + '.txt'

		if size == 0:

			op = 'w+'

		else:

			op = 'a+'

		operator = open(filename,op)

		operator.write(result+'\n')

		operator.close()

	return filename,name		



def PrintBinary(out):										#@Translate the picture to the binnary string

	for y in range(out.height):

		result = ''

		for x in range(out.width):

			result = result + str(out.getpixel((x,y)))

		print result



def BinaryImg(path):										#@First translate the picture into the gray one 

	image = Image.open(path)								#@And the translate the picture into the binnary one

	image.putpixel((0,4),0)

	toGray = image.convert('L')

	table = GrayToBinary()

	out = toGray.point(table,'1')

	return out


def GetFeature(img):										#@Get the feature from the image

	width,height = img.size 								#@In order to return the special string for the libsvm

	feature = []

	height = 10

	for y in range(height):

		xSize = 0

		for x in range(width):

			if img.getpixel((x,y)) == 0:

				xSize = xSize + 1

		feature.append(xSize)

	for x in range(width):

		ySize = 0

		for y in range(height):

			if img.getpixel((x,y)) == 0:

				ySize = ySize + 1

		feature.append(ySize)

	return feature
	
def DealImg(getPath):

	for number in range(10):

		getImg = os.walk('Image/' + str(number) +'/')

		for parent,dirnames,filenames in getImg:

			for filename in filenames:

				image = BinaryImg(parent + filename)

				feature = GetFeature(image)

				single = 0

				result = '' + str(number)

				for line in feature:

					single = single + 1

					result = result + ' ' + str(single) + ':' + str(line)

				operator = open('data.txt','a+')

				operator.write(result+'\n')

				operator.close()


def TrainSvmModel():								#@Trainning function

	y,x = svm_read_problem('data.txt')

	model = svm_train(y,x)

	svm_save_model('svm.txt',model)					#@The model file will be save in the file 'svm.txt'


def SvmModelTest(filename,name):					#@Verify the code,and save the result in the file.

	y,x = svm_read_problem(filename)

	model = svm_load_model('svm.txt')

	label,acc,val = svm_predict(y,x,model)

	result = ''

	for item in label:

 		result = result + str(int(item))

 	print "The code is " + result

 	filename = open('result.txt','a+')

 	filename.write(result + '\n')

 	filename.close()





def main():

	getPath,mode = ArgModule()

	if isinstance(getPath,basestring):						#Verify or Trainning the machine

		out = BinaryImg(getPath)

		filename,name = SingleDealImg(out,getPath,mode)

		SvmModelTest(filename,name)

		os.remove(filename)


	else:													#Split the picture

		for path in getPath:

			out = BinaryImg(path)

			ApiDenoise(out,path)

			print path + ' is Done'



if __name__ == '__main__':

	main()