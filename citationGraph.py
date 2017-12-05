'''
 citation graph creator
 use this to get the citations for a given text files of papers and abstracts
 we put the name of this text file as COPD
'''

import numpy as numpy
import time
import dataRetrieval
import pickle
import util
import concurrent.futures

# COPD_FILE = 'guanAbstracts.txt'
# COPD_FILE = 'copdsmall.txt'
COPD_FILE = 'copd_pre2010.txt'
TYPE = 'tfidf'
TYPE2 = 'count'
TYPES = [TYPE, TYPE2]
ABSTRACT_DICT_FILE = 'abstractVectors.npy'
CITATION_FILE = 'citations.npy'
MAX_WORKERS = 20

def main():
	try:
		raise Exception('Don\'t load the file!')
		with open(ABSTRACT_DICT_FILE, 'rb') as f:
			abstractVectorDictList = pickle.load(f)
	except Exception as e:
		print('Files for article dictionaries not found - Generating from scratch')
		abstractVectorDictList, _, paperAuthorDict, paperDateDict, __ = dataRetrieval.getAllData([COPD_FILE], TYPES)
		with open(ABSTRACT_DICT_FILE, 'wb') as f:
			pickle.dump(abstractVectorDictList, f)
	print('Retrieved all data')
	titles = list(abstractVectorDictList[0])
	print(titles)

	citationDict = {}
	with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
		future_to_article = {executor.submit(util.getCitations, title): title for title in titles}
		for future in concurrent.futures.as_completed(future_to_article):
			articleTitle = future_to_article[future]
			try:
				data = future.result()
			except Exception as exc:
				print('%r generated an exception: %s' % (articleTitle, exc))
			else:
				print('Graph retrieved for %s' % articleTitle)
				if data is None:
					print('But the data is none')
				citationDict[articleTitle] = data
	with open(CITATION_FILE, 'wb') as f:
		pickle.dump(citationDict, f)
	print(citationDict)

main()
