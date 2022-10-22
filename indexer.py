import sys
import os
import gzip
import json
from collections import defaultdict

'''
inputFile - file to be indexed
queriesFile - file of queries
outputFolder - location to store result
'''
def main(inputFile,queriesFile,outputFolder):
    #convert inputfile to list of dicts
    with gzip.open(inputFile,'rt',encoding='utf-8') as f:
        input_list = json.load(f)

    #inverted list with format: {'term': [(docId,positions[])]}
    inv_index = defaultdict(list)
    
    '''
    process scenes to create index list
    playId - use when retrieving plays
    sceneId - use for retrieving scenes
    sceneNum - 
    text - text of the scene
    '''
    for doc in input_list:
        text = doc['text'].split()
        docId = doc['sceneId']
        position = 0
        postings = defaultdict(list)
        
        #get positions of each term
        for term in text:
            postings[term].append(position)
            position += 1

        for key,val in postings:
            inv_index[key].append((docId,val))

    '''
    Add an appropriate API to your index to enable accessing the vocabulary, 
    term counts, document counts and other statistics that you will require to 
    perform the query evaluation activities. 
    '''
    def term_count(term):
        count = 0

        for posting in inv_index[term]:
            count += len(posting[1])

        return count

    def doc_count(term):
        return len(inv_index[term])

    '''
    Run boolean queries
    Either return by PlayID or SceneID
    queryname - for each queryname create a file called results/queryname.txt
    scenePlay - either scene or play, to indiciate which id is used
    AndOr 
    wordPhrase1 wordPhrase2 … wordPhraseN
    '''
    with open(queriesFile) as f:
        queries = f.readlines()
    
    for line in queries:
        args = line.split()
        queryname = args[0]
        sceneplay = args[1]
        AndOr = args[2]
        wordPhrases = args[3:]

    return



if __name__ == '__main__':
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else 'shakespeare-scenes.json.gz'
    queriesFile = sys.argv[2] if argv_len >= 3 else 'trainQueries.tsv'
    outputFolder = sys.argv[3] if argv_len >= 4 else 'results/'
    if not os.path.isdir(outputFolder):
        os.mkdir(outputFolder)
    main(inputFile,queriesFile,outputFolder)