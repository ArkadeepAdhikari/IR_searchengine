import pickle
import os
import threading

'''
a-d - &1
e-l - &2
m-r - &3
s-z - &4

aceimpst -> a_1_2_2_3
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
    
    mydict = {}
    index = open(folder + char + '.txt', 'r')
    index.readline()
    line = index.readline()
    
    while line:
        terms = line.split(":")
        key = terms[0]
        length = len(key)
        hasdigits = False
        if key == '}':
            break
        if key[0].isdigit():
            hasdigits = True
        arr = [0, 0, 0, 0]
        
        for p in range(4):
            if p + 1 <= length - 1:
                if key[p + 1].isdigit():
                    hasdigits = True
                else :
                    arr[p] = getgroup(key[p + 1])
        if hasdigits:
            line = index.readline()
            continue
        filename = getfilename(outputpath, char, arr)
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
    d = {}
    for i in range(26):
        d[i] = threading.Thread(target=getdict, args=(chr(i + ord('a')), 'scores/'))
        d[i].start()
    for i in range(26):
        d[i].join()
