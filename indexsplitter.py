if __name__ == '__main__':
    folder = 'scores_splits/'
    char = 'a'
    myfile = open(folder + 'a.txt', 'w+')
    myfile.write('{\n')
    
    mydict = {}
    index = open('new_scores.txt', 'r')
    index.readline()
    line = index.readline()
    cnt = 0
    while line:
        terms = line.split(":")
        key = terms[0]
        length = len(key)
        hasdigits = False
        if key == '}':
            break
        if key[0].isdigit(): 
            hasdigits = True
        else :
            for p in range(4):
                if p + 1 <= length - 1:
                    if key[p + 1].isdigit():
                        hasdigits = True
                        break
                
        if hasdigits:
            line = index.readline()
            continue
        if key[0] == char:
            myfile.write(line)
            myfile.flush()
            
            cnt += 1
            if cnt % 50000 == 0:
                print(cnt)
            
        else:
            myfile.write("}")
            myfile.flush()
            myfile.close()
            
            print(char)

            mydict.clear()
            char = key[0]
            
            filename = folder + char + '.txt'
            myfile = open(filename, 'w+')
            myfile.write('{\n')
            
        line = index.readline()
