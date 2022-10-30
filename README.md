## Breakdown
If it is not blatantly obvious (to a human who is not you), please indicate where in your source code the indexing happens and where the query evaluation happens.
- Indexing: ```line 26 -> line 39```
- Query evaluation
  - Reading query from input and writing to output: ```line 121 -> line 139```
  - Executing query: function name ```bool_query``` at ```line 88 -> line 111```
    - Helper function to handle phrases: function name ```get_wordphrase``` at ```line 59 -> 85```

## Description 
Provide a description of system, design tradeoffs, etc., that you made. Focus on how you implemented the indexing and its data structures and on how you implemented query evaluation.
- Indexing
  - Created an inverse index using a defaultdict(list)
  - For each scene create a postings list of type defaultdict(list)
    - For each term in the text, add the position of that word in that text to postings
  - Once postings are created, for each word in postings, append a tuple of (sceneId,playId,positions) to inverse index of that term\
- Query evaluation
  - Query evaluation generates sets for executing queries
    - Sets in python have built in & and | functionality, this is why I chose to use them
  - For the first wordphrase, initialize the query_res set to be all scenes/plays containing that word phrase
    - Use a variable ```scene_play``` input to indicate which index the relevant docId is in (either sceneId or playId)
    - To handle phrases, use the ```get_wordphrases``` function
      - Creates a set ```multiword``` of all scenes containing the first word, tuples of (sceneId,playId,position)
      - For each subsequent word, checks if (sceneId,playId,pos-1) is in multiword, if so adds it to a set ```curr_res```
      - Multiword is set to a copy of curr_res, and the next word is checked
  - For each subsequent word/phrase, create a set ```phrase_ids```, for phrases use get_wordphrase to handle phrases
  - If wordphrase is just a word, then create a set of the appropriate ids for each posting in the inverted index for that word
  - Depending on AndOr value, set query res to be query_res & phrase_ids or query_res | phrase_ids

## Libraries 
List the software libraries you used, and for what purpose. Implementation must be your own work. If you are thinking of using any other libraries for this assignment, please send us an email to check first.
- sys: allowing custom input according to P3 instructions
- os: create folder for outputting results
- gzip: open the gzip files
- json: convert shakespeare-scenes.json into dict
- defaultdict: make creating inverse index and posting lists easier

## Dependencies
Provide instructions for downloading dependencies of the code. Not expecting anything here.
- Python version >= 3.9.13

## Building 
Provide instructions for building the code.
- Download the code
- Make sure Python version >= 3.9.13

## Running
Provide instructions for running the code
- CD into the directory which contains ```indexer.py```
- In terminal, run the command "python indexer.py" followed by optional args: ```"inputFile" "queriesFile" "outputFolder"```
