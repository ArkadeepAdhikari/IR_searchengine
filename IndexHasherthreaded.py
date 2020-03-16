import time
import pickle
import os
import threading
'''
one_gram

en - 8700
e* - 
ma-mh -
mh-mz -
sa-sl -
sm-sz -

2_gram
a-d - &1
e-l - &2
m-r - &3
s-z - &4

a_1_1_1_1

* _ _ _ _   
* d
* e
* l
*  


aa a
aa b
aa c
aa z
aa0a
aa0b

aceimpst

a_2_3_1_4

a e m _ s

a l r d z




* _ _ _ _
* _ _ _ d

* _ _ _ _
* d z z z

* d
* e

'''

ref = [[' ', 'd'], ['e', 'l'], ['m', 'r'], ['s', 'z']]


def belongsto(val, group):
    if val >= ref[group][0] and val <= ref[group][1]:
        return True
    else:
        return False   


def getgroup(val):
    for p in range(4):
        if val >= ref[p][0] and val <= ref[p][1]:
            return p


def getdict(char, outputpath):
    print('starting ' + char)
    folder = 'scores_splits/'
    # char = 'a'
    # arr = [0, 0, 0, 0]
    # filename = getfilename(folder, char, arr)
    
    mydict = {}
    index = open(folder + char + '.txt', 'r')
#     print(folder + char + '.txt')
    index.readline()
    line = index.readline()
    
    while line:
        terms = line.split(":")
        key = terms[0]
        length = len(key)
        belongs = False
        hasdigits = False
        if key == '}':break
        if key[0].isdigit(): hasdigits = True
        # char = key[0]
        arr = [0, 0, 0, 0]
        
        for p in range(4):
            if p + 1 <= length - 1:
                if key[p + 1].isdigit():
                    hasdigits = True
                else :
                    arr[p] = getgroup(key[p + 1])
        if hasdigits:
            # filename = folder + 'digits.pickle'   
            # ignore
            line = index.readline()
            continue
        filename = getfilename(outputpath, char, arr)
#         print(filename)
        if(os.path.exists(filename)):
            with open(filename, 'rb') as handle:
                mydict = pickle.load(handle)
        else :
            mydict = {} 
                   
        mydict[terms[0]] = terms[1]
        
        pklfile = open(filename, 'wb')
        pickle.dump(mydict, pklfile, protocol=pickle.HIGHEST_PROTOCOL)
        pklfile.close()
        line = index.readline()
    return mydict    

        
def getfilename(folder, char, arr):
    filename = folder + char
    for i in arr:
        filename += '_' + str(i + 1)
    filename += '.pickle'
    return filename    


if __name__ == '__main__':
#     with open('scores/a_4_4_4_4.pickle', 'rb') as handle:
#         mydict = pickle.load(handle)
#     print(sorted(mydict.keys()))   
    
    d = {}
    for i in range(26):
        d[i] = threading.Thread(target=getdict, args=(chr(i + ord('a')), 'scores/'))
        d[i].start()
    for i in range(26):
        d[i].join()

