import os
import math


def getContent(f_gram, f_score):
    gram_content = f_gram.readline()[:-1].split(':')
    score_content = f_score.readline()[:-1].split(':')
    old_score_content = score_content
    
    while gram_content and score_content and gram_content[0] != score_content[0]:
        
        #print(gram_content + '    ' + str(score_content[0]))
        score_content = f_score.readline()[:-1].split(':')
        
        if not score_content:
            print('Reached EOF looking for ' + gram_content[0])
            gram_content = f_gram.readline()[:-1].split(':')
            f_score.seek(0, 0)
            score_content = f_score.readline()[:-1].split(':')
            while score_content != old_score_content:
                score_content = f_score.readline()[:-1].split(':')
    return gram_content, score_content            


def updateScores():
    doc_dict = {}
    dict_f = open('doc_dict.txt', 'r')
    dict_f.readline()
    val = dict_f.readline()[:-1].split(':', 1)
    while len(val) == 2:
        numWords = val[1].split('|')[1]
        doc_dict[val[0]] = int(numWords)
        val = dict_f.readline()[:-1].split(':', 1)
    numDoc = len(doc_dict.keys())
    
    f_gram = open('onegrams.txt', 'r')
    f_score = open('scores.txt', 'r')
    new_score = open('new_scores.txt', 'w+')
    new_score.write('{\n')
    
    gram_content = f_gram.readline()
    score_content = f_score.readline()
    
    gram_content, score_content = getContent(f_gram, f_score)
    count = 0
                
    if gram_content != '}' : 
    
        score_list = score_content[1].strip('[]').split(', ')
        score_dict = {}    
        for score in score_list:
            parts = score.strip('\'').split('|')
            if (parts[0] in score_dict and parts[1] > score_dict[parts[0]]) or parts[0] not in score_dict:
                score_dict[parts[0]] = parts[1]
        if len(score_dict.keys()) > 2 :
            w = 2 + 1
            pass
        
        while len(gram_content) == 2:
            val_list = gram_content[1].strip('[]').split(', ')
            
            new_score.write(gram_content[0] + ':[')
            first_element = True
            
            currDoc = -1
            tf = 0
            for val in val_list:
                docId = val.strip('\'').split('|')[0]
                if(docId != currDoc):
                    if(currDoc != -1):
                        tfidf = round((tf * 1.0 / float(doc_dict[currDoc])) * math.log(numDoc / (1 + len(score_dict.keys()))), 3)
                        if currDoc in score_dict:
                            currScore = score_dict[currDoc]
                        else:
                            print('Score not found' + str(currDoc))
                            print(gram_content)
                            print(score_content)
                            currScore = 1    
                        final_score = tfidf * float(currScore)
                        if not first_element:
                            new_score.write(', ')
                        new_score.write(str(currDoc) + '|' + str(final_score))
                        first_element = False
                    tf = 0
                    currDoc = docId
                tf += 1
            if tf > 0 :
                tfidf = round((tf * 1.0 / float(doc_dict[currDoc])) * math.log(numDoc / (1 + len(score_dict.keys()))), 8)
                if currDoc in score_dict:
                    currScore = score_dict[currDoc]
                else:
                    print('Score not found' + str(currDoc))
                    print(gram_content)
                    print(score_content)
                    currScore = 1    
                final_score = tfidf * float(currScore)
                if not first_element:
                    new_score.write(', ')
                new_score.write(str(currDoc) + '|' + str(final_score))
            new_score.write(']\n')
            count += 1
            if count % 20000 == 0:
                print(count)
            gram_content, score_content = getContent(f_gram, f_score)
            score_list = score_content[1].strip('[]').split(', ')
            score_dict = {}    
            for score in score_list:
                parts = score.strip('\'').split('|')
                if (parts[0] in score_dict and parts[1] > score_dict[parts[0]]) or parts[0] not in score_dict:
                    score_dict[parts[0]] = parts[1]
            
    new_score.write('}')
    new_score.flush()    


if __name__ == '__main__':
    updateScores()
