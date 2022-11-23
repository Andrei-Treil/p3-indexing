## Breakdown
If it is not blatantly obvious (to a human who is not you), please indicate where in your source code the querying happens, including where the BM25 and QL scoring occur.
- Indexing: ```line 19 -> line 54```
- Helper Variables after indexing: ```line 57 -> line 74```
- Query evaluation
  - Reading query from input and writing to output: ```line 241 -> line 264```
  - BM25: ```line 145 -> line 173```
  - QL: ```line 184 -> line 231```

## Description 
Provide a description of system, design tradeoffs, etc., that you made. Focus on how any changes you made to the inverted list from P3 to handle these queries and how you implemented scoring and ranking.
- Indexing
  - Added length of the scene and play to inverse index
  - Added global variables to keep track of total number of words in collection, as well as total number of words in each scene/play
- Scoring/Ranking
  - BM25
    - For each term in the query, iterate through the inverted index for that word
    - Create a set based off the index to produce collection of documents with relevant information
      - Scene sets contain sceneId, # of term occurences in the scene, length of the scene
      - Play sets contain playId, # of term occurences in the play, length of the play
    - For each document, use the information to calculate the score of the document for the current query term, add score to corresponding doc id in res dict
  - QL
    - For each word in the query, calculate cqi and check if a document which was previously ranked is going to be ranked in this iteration
      - For all documents which were previously ranked but will not be ranked in this iteration, increase their score by calculating the dirichlet score using fqi = 0, and the document's length
    - For each document in the set of postings for the current word, check if the document has been ranked
    - If a document has not been ranked, calculate score of that doc for each previous query term using fqi = 0 and the value of cqi/C from  each previous term

## Libraries 
List the software libraries you used, and for what purpose. Implementation must be your own work. If you are thinking of using any other libraries for this assignment, please send us an email to check first.
- sys: allowing custom input according to P3 instructions
- gzip: open the gzip files
- json: convert shakespeare-scenes.json into dict
- defaultdict: make creating inverse index and posting lists easier
- math: math.log

## Dependencies
Provide instructions for downloading dependencies of the code. Not expecting anything here.
- Python version >= 3.9.13

## Building 
Provide instructions for building the code.
- Download the code
- Make sure Python version >= 3.9.13

## Running
Provide instructions for running the code
- CD into the directory which contains ```query.py```
- In terminal, run the command "python query.py" followed by optional args: ```"inputFile" "queriesFile" "outputFile"```
