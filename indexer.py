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
    text - text of the scene
    '''
    for doc in input_list['corpus']:
        text = doc['text'].split()
        sceneId = doc['sceneId']
        playId = doc['playId']
        position = 0
        postings = defaultdict(list)
        
        #get positions of each term
        for term in text:
            postings[term].append(position)
            position += 1

        for key,val in postings.items():
            inv_index[key].append((sceneId,playId,val))

    '''
    Add an appropriate API to your index to enable accessing the vocabulary, 
    term counts, document counts and other statistics that you will require to 
    perform the query evaluation activities. 
    '''
    def term_count(term):
        count = 0

        for posting in inv_index[term]:
            count += len(posting[2])

        return count

    def doc_count(term):
        return len(inv_index[term])

    #handle multi word phrases
    #scene_play = 0 if scenes, 1 if plays
    def get_wordphrase(wordphrase,scene_play):
        #set of docIds that contain wordphrase
        query_res = set()
        
        multiword = set()
        for sceneId,playId,positions in inv_index[wordphrase[0]]:
            for pos in positions:
                multiword.add((sceneId,playId,pos))

        wordphrase.pop(0)
        for word in wordphrase:
            curr_res = set()
            for sceneId,playId,positions in inv_index[word]:
                for pos in positions:
                    #check if word occurs directly after previous hit
                    if (sceneId,playId,pos-1) in multiword: 
                        curr_res.add((sceneId,playId,pos))

            multiword = curr_res.copy()

            if len(multiword) == 0:
                return multiword

        for tup in multiword:
            query_res.add(tup[scene_play])

        return query_res

    #scene_play = 0 if scene, 1 if play
    def bool_query(and_or,phrases,scene_play):
        #set of docids which match the query
        query_res = set()
        for phrase in phrases:
                multiphrase = phrase.split()
                #if first wordphrase, get all results for that wordphrase
                if len(query_res) == 0:
                    if len(multiphrase) > 1:
                        query_res = get_wordphrase(multiphrase,scene_play)      
                    else:
                        query_res = set([posting[scene_play] for posting in inv_index[phrase]])
                    continue
                
                if len(multiphrase) > 1:
                    phrase_ids = get_wordphrase(multiphrase,scene_play)
                else:
                    phrase_ids = set([posting[scene_play] for posting in inv_index[phrase]])
                
                if and_or.lower() == "and":
                    query_res = query_res & phrase_ids
                else:
                    query_res = query_res | phrase_ids

        return query_res

    '''
    Run boolean queries
    Either return by PlayID or SceneID
    queryname - for each queryname create a file called results/queryname.txt
    scenePlay - either scene or play, to indiciate which id is used
    AndOr 
    wordPhrase1 wordPhrase2 … wordPhraseN - seperated by tabs, words seperated by spaces indicate a multiword phrase
    '''
    with open(queriesFile) as f:
        queries = f.readlines()
    
    for line in queries:
        line = line.strip('\n')
        args = line.split('\t')
        queryname = args[0]
        sceneplay = args[1]
        AndOr = args[2]
        wordPhrases = args[3:]

        out_path = outputFolder + queryname + ".txt"
        with open(out_path,'w') as f:
            if sceneplay == "scene":
                results = bool_query(AndOr,wordPhrases,0)
            else:
                results = bool_query(AndOr,wordPhrases,1)
            for elem in results:
                f.write(elem + "\n")


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