# citationProject
Citation Project for CS221 and CS229

To get the citations, you need to run dataCitation.py
You must manually fill in the START_INDEX and START_INDEX_LIST for each topic type
Then, you must run dataCitation.py for each different START_INDEX


Once you have all the citations, you can run experiments.py



To change the file and topic used, change TOPIC and DATA_FILES in constants.py
Make sure to decompress the zip files into normal txt files

e.g.
TOPIC = 'copd'
DATA_FILES = ['copd_pre2010.txt']

to

TOPIC = 'alzheimer'
DATA_FILES = ['alzheimer_pre2010.txt']
