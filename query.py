import sys
import os
import gzip
import json
from collections import defaultdict,Counter
import math

'''
inputFile - file to be indexed
queriesFile - file of queries
outputFolder - location to store result
'''
def main(inputFile,queriesFile,outputFile):
    #convert inputfile to list of dicts
    with gzip.open(inputFile,'rt',encoding='utf-8') as f:
        input_list = json.load(f)

    #inverted list with format: {'term': [(docId,positions[])]}
    inv_index = defaultdict(list)
    
    #counter to count number of plays and scenes
    scene_counter = defaultdict(int)
    play_counter = defaultdict(int)

    #count doc length
    scene_length = defaultdict(int)
    play_length = defaultdict(int)

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

        scene_counter[sceneId] += 1
        play_counter[playId] += 1
        scene_length[sceneId] += len(text)
        play_length[playId] += len(text)
       
        position = 0
        postings = defaultdict(list)
        
        #get positions of each term
        for term in text:
            postings[term].append(position)
            position += 1

        for key,val in postings.items():
            inv_index[key].append((sceneId,playId,val,text))
        
    NUM_SCENES = len(scene_counter)
    NUM_PLAYS = len(play_counter)


    ###################################
    #FIX THIS LATER

    SCENE_WORDS = 0
    for val in scene_length.values():
        SCENE_WORDS += val


    LEN_SCENES = SCENE_WORDS/NUM_SCENES

    PLAY_WORDS = 0
    for val in play_length.values():
        PLAY_WORDS += val

    LEN_PLAYS = PLAY_WORDS/NUM_PLAYS

    DOC_LEN_AVG = (LEN_SCENES,LEN_PLAYS)
    DOC_WORDS = (SCENE_WORDS,PLAY_WORDS)

    ####################################


    #handle multi word phrases
    #scene_play = 0 if scenes, 1 if plays
    def get_wordphrase(wordphrase,scene_play):
        #set of docIds that contain wordphrase
        query_res = set()
        
        multiword = set()
        for sceneId,playId,positions,text in inv_index[wordphrase[0]]:
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
    k1 = 1.8, k2 = 5, b = 0.75
    Execute bm25 ranking with the above values
    log(N-ni+0.5 / ni+0.5) * (k1+1)fi/K+fi * (k2+1)qfi/k2+qfi
    N - total docs
    ni - number of documents term i appears in
    fi - frequency of term i in the document
    qfi - frequency of term i in the query
    K - k1((1-b)+b*(dl/avg_dl))
    '''
    def bm25(query,scene_play):
        res = defaultdict(int)

        k1 = 1.8 
        k2 = 5
        b = 0.75

        query_terms = Counter(query)

        for word in query:
            if scene_play == 0:
                N = NUM_SCENES
            else:
                N = NUM_PLAYS

            qfi = query_terms[word]
            #docs containing word
            docs = [(posting[scene_play],len(posting[2]),len(posting[3])) for posting in inv_index[word]]
            #docs = inv_index[word]
            ni = len(docs)

            for id,fi,dl in docs:
                K = k1*((1-b)+(b*dl/DOC_LEN_AVG[scene_play]))
                res[id] += math.log(((N-ni+0.5) / (ni+0.5))) * (((k1+1)*fi)/(K+fi)) * (((k2+1)*qfi)/(k2+qfi))
                
        return sorted(res.items(),key=lambda x: x[1],reverse=True)


    '''
    mu = 300
    log((fqi,D + mu * cqi/|C|) / (|D|+mu))
    |D| - # of word occurrences in the document
    |C| - # of word occurrences in the collection
    fqi,D - # of times a word qi occurs in document D
    cqi - # of times a query word occurs in the collection
    '''
    def ql_dirichlet(query,scene_play):
        res = defaultdict(int)
        #store len of encountered docs
        prev_ids = defaultdict(int)
        #store cqi/C for previous query words
        query_terms = defaultdict(int)
        mu = 300
        C = DOC_WORDS[scene_play]      


        for word in query:
            old_ids = prev_ids.copy()
            curr_ids = defaultdict(int)

            cqi = 0
            for post in inv_index[word]:
                curr_ids[post[scene_play]] += len(post[2])
                try:
                    del old_ids[post[scene_play]]
                except:
                    pass
                cqi += len(post[2])
            
            #if a prev doc not encountered in postings, add score with fqi = 0
            for old_doc,size in old_ids.items():
                res[old_doc] += math.log((mu * cqi/C) / (size + mu))

            query_terms[word] += cqi/C

            docs = [(posting[scene_play],len(posting[2]),len(posting[3])) for posting in inv_index[word]]

            for id,fqi,D in docs:
                prev_ids[id] = D

                #if first time encountering doc, retroactively add scores for prev words to this doc
                if res[id] == 0 and len(query_terms) > 1:
                    for term,val in query_terms.items():
                        res[id] += math.log((mu * val) / (D + mu))

                res[id] += math.log((fqi + (mu * cqi/C)) / (D + mu))


        return sorted(res.items(),key=lambda x: x[1],reverse=True)

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
        queryName = args[0]
        scenePlay = 0 if args[1] == "scene" else 1
        qType = args[2].lower()
        wordPhrases = args[3:]

        out_path = outputFile
        with open(out_path,'a') as f:
            if qType == "bm25":
                results = bm25(wordPhrases,scenePlay)
            else:
                results = ql_dirichlet(wordPhrases,scenePlay)

            rank = 1
            for id,score in results[:100]:
                f.write(queryName + " skip " + id + " " + str(rank) + " " + str(score) + " atreil@umass.edu\n")
                rank += 1

    return



if __name__ == '__main__':
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else 'shakespeare-scenes.json.gz'
    queriesFile = sys.argv[2] if argv_len >= 3 else 'trainQueries.tsv'
    outputFile = sys.argv[3] if argv_len >= 4 else 'trainQueries.results'
    main(inputFile,queriesFile,outputFile)