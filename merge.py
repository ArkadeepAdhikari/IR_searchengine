# import Queue

import threading
import os


def merge(file1, file2, thread, outputpath):
    finalFile = open(outputpath+'/' + 'final_merged_file'+str(thread)+'.txt', 'w+')

    if not file2:
        file1 = open(file1, 'r')
        while True:
            l1 = file1.readline()
            finalFile.write(l1)
            if not l1: break
        finalFile.flush()
        #finalFile.writelines([l for l in open(file1).readlines()])

    else:

        file1 = open(file1, 'r')
        file2 = open(file2, 'r')
        finalFile.write('{' + '\n')
        file1.readline()
        file2.readline()
        content1 = file1.readline()[:-1].replace('}', '').split(':')
        content2 = file2.readline()[:-1].replace('}', '').split(':')
        key1, key2, list1, list2 = None, None, None, None

        if len(content1) == 2 and len(content2) == 2:
            key1, list1, key2, list2 = content1[0], content1[1], content2[0], content2[1]
            #print(key1, list1, key2, list2)
        while len(content1) == 2 and len(content2) == 2:
            finalkey, finallist = None, []
            if key1 < key2:
                finalkey, finallist = key1, list1
                content1 = file1.readline()[:-1].replace('}', '').split(':')
                if len(content1) == 2:
                    key1, list1 = content1[0], content1[1]
                else:
                    key1, list1 = None, None
            elif key1 == key2:
                finalkey, finallist = key1, list1[:-1] + ', ' + list2[1:]
                content1 = file1.readline()[:-1].replace('}', '').split(':')
                content2 = file2.readline()[:-1].replace('}', '').split(':')
                if len(content1) == 2:
                    key1, list1 = content1[0], content1[1]
                else:
                    key1, list1 = None, None
                if len(content2) == 2:
                    key2, list2 = content2[0], content2[1]
                else:
                    key2, list2 = None, None
            else:
                finalkey, finallist = key2, list2
                content2 = file2.readline()[:-1].replace('}', '').split(':')
                if len(content2) == 2:
                    key2, list2 = content2[0], content2[1]
                else:
                    key2, list2 = None, None

            finalFile.write(finalkey + ':' + str(finallist) + '\n')
            finalFile.flush()

        res_file, res_key, res_list = file1, key1, list1

        if key2:
            res_file, res_key, res_list = file2, key2, list2
        while res_key:
            finalFile.write(res_key + ':' + str(res_list))
            res_con = res_file.readline()[2:].replace('}', '').split(':')
            if len(res_con) == 2:
                res_key, res_list = res_con[0], res_con[1]
            else:
                res_key, res_list = None, None
        finalFile.write('}')


d = {}
wd = r'F:\UCI\Q5\Courses\IR'
os.chdir(wd)
if wd == r'F:\UCI\Q5\Courses\IR':
    pathfiles = [filename for filename in os.listdir(wd) if filename.startswith("threegrams")]
else:
    pathfiles = os.listdir(wd)

outputpath = wd + '/' + 'threegrams_output'
os.mkdir(outputpath)
n = len(pathfiles)
print('Merging files:'+ str(pathfiles))
for i in range(n//2 + 1):
    if n == 2:
        merge(pathfiles[0], pathfiles[1], 1, outputpath)
        break
    if i == n//2:
        if n%2 != 0:
            d[str(i)] = threading.Thread(target = merge,args = (pathfiles[i], None, i + 1, outputpath))
    else:
        d[str(i)] = threading.Thread(target = merge,args = (pathfiles[i], pathfiles[n - 1 - i], i + 1, outputpath))
    if d.get(str(i),None):
        d[str(i)].start()
for i in range(n//2 + 1):
    if n != 2:
        th = d.get(str(i), None)
        if th:
            th.join()
