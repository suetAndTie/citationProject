PM_REQUEST_URL = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=Co-CitationProject&email=guana@stanford.edu&ids='
PMC_REQUEST_URL_PRE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pmc&linkname=pmc_refs_pubmed&id='
PMC_REQUEST_URL_POST = '&tool=Co-CitationProject&email=guana@stanford.edu'

# Number of max workers for multi-threading
MAX_WORKERS = 1

# topic of files to use and a list with the file in it
TOPIC = 'copd'
DATA_FILES = ['copd_pre2010.txt']

# Percent of data to allocate to train (0.6), dev (0.2), and test (0.2) set
PERCENT_TRAIN = 0.6
PERCENT_DEV = 0.2
