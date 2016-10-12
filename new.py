import os

'''
for i in range(1,10000):

	print i

	command = 'python VerifyCode.py -f image/bmp/' + str(i) + '.bmp -m r'

	os.system(command)

'''

filename = open('result.txt','r')

lines = filename.readlines()

num = 1

result = 0

for line in lines:

	get = num * int(line)

	result = result + get

	num = num + 1

print result