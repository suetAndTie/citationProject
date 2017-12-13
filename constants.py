PM_REQUEST_URL = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=Co-CitationProject&email=guana@stanford.edu&ids='
PMC_REQUEST_URL_PRE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pmc&linkname=pmc_refs_pubmed&id='
PMC_REQUEST_URL_POST = '&tool=Co-CitationProject&email=guana@stanford.edu'

PM_CITEDBY_URL_PRE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id='
PM_CITEDBY_URL_POST = '&tool=Co-Citation&email=ttsue@stanford.edu'



'''
Constants for both experiments.py and dataCitation.py
'''
# Number of max workers for multi-threading
MAX_WORKERS = 20

# topic of files to use and a list with the file in it
TOPIC = 'copd'
DATA_FILES = ['copd_pre2010.txt']




'''
Constatns for experiments.py
'''

# Percent of data to allocate to train (0.6), dev (0.2), and test (0.2) set
PERCENT_TRAIN = 0.6
PERCENT_DEV = 0.2




'''
Constants for getting data citation information from dataCitation.py
We are aiming to get NUM_PAPER_CITATIONS papers per run
'''

# make this true if you want to get the citations for START_INDEX
GET_CITATIONS = False

# make this true if you are done getting the citations and want to merge them all
# into a final publication list
MERGE_PUBLIST = False

# CHANGE THIS FOR EACH RUN
# refers to which start index we are using from START_INDEX_LIST
# From 0 to 35
START_INDEX = 0

# number of papers we are trying to get citations for for each run
NUM_PAPERS_CITATION = 100
