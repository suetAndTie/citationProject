#logistic regression

import util
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as metrics
import dataRetrieval
import pickle
import numpy as np
import time
import urllib2
import xml.etree.ElementTree as ET

# COPD_FILE = 'copd.txt'
# COPD_FILE = 'copdsmall.txt'
COPD_FILE = 'copd_pre2010.txt'
TYPE = 'tfidf'
TYPE2 = 'count'
TYPES = [TYPE, TYPE2]
ABSTRACT_DICT_FILE = 'abstractVectors.npy'
CITATION_DICT_FILE = 'citations.npy'
AUTHOR_DICT_FILE = 'authors.npy'
DATE_DICT_FILE = 'dates.npy'
PAIRLIST_FILE = 'pairs.npy'
INPUT_VECTORS_FILE = 'input.npy'
COUNT_INPUT_VECTORS_FILE = 'countInput.npy'
OUTPUT_LABELS_FILE = 'output.npy'
RETRO_CITATION_FILE = 'retroCitations.npy'
PM_REQUEST_URL = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=Co-CitationProject&email=guana@stanford.edu&ids='
PMC_REQUEST_URL_PRE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pmc&linkname=pmc_refs_pubmed&id='
PMC_REQUEST_URL_POST = '&tool=Co-CitationProject&email=guana@stanford.edu'

LOG_REG_MODEL_FILE = 'logRegModel.npy'
CONTROL_LOG_REG_MODEL_FILE = 'controlLogRegModel.npy'
MLP_MODEL_FILE = 'mlpModel.npy'
CONTROL_MLP_MODEL_FILE = 'controlmlpModel.npy'



# need to find way to generate training output data
# need to split data into training and test data
def main():
	# generate feature extractor, output data
	numTraining = 0.7 # change this to change proportion of data that should be used for training data
	try:
		# raise Exception('hi')
		with open(ABSTRACT_DICT_FILE, 'rb') as f:
			abstractVectorDictList = pickle.load(f)
		with open(AUTHOR_DICT_FILE, 'rb') as f:
			paperAuthorDict = pickle.load(f)
		with open(DATE_DICT_FILE, 'rb') as f:
			paperDateDict = pickle.load(f)
	except Exception as e:
		print('Files for article dictionaries not found - Generating from scratch')
		abstractVectorDictList, _, paperAuthorDict, paperDateDict, pmidDict = dataRetrieval.getAllData([COPD_FILE], TYPES)
		with open(ABSTRACT_DICT_FILE, 'wb') as f:
			pickle.dump(abstractVectorDictList, f)
		with open(AUTHOR_DICT_FILE, 'wb') as f:
			pickle.dump(paperAuthorDict, f)
		with open(DATE_DICT_FILE, 'wb') as f:
			pickle.dump(paperDateDict, f)
	print('Retrieved all data')
	try:
		with open(PAIRLIST_FILE, 'rb') as f:
			pairList = pickle.load(f)
	except Exception as e:
		print('Files for pair list not found - Generating from scratch')
		keys = list(abstractVectorDictList[0])
		pairList = [(keys[i], keys[j]) for i in xrange(len(keys)) for j in xrange(i + 1, len(keys))]
		with open(PAIRLIST_FILE, 'wb') as f:
			pickle.dump(pairList, f, pickle.HIGHEST_PROTOCOL)
	print('Created pair list')
	print(len(pairList))

	try:
		# raise Exception('hi')
		with open(INPUT_VECTORS_FILE, 'rb') as f:
			inputVectors = pickle.load(f)
		with open(COUNT_INPUT_VECTORS_FILE, 'rb') as f:
			countInputVectors = pickle.load(f)
		with open(OUTPUT_LABELS_FILE, 'rb') as f:
			outputLabels = pickle.load(f)
	except Exception as e:
		print('Files for feature vectors and output labels not found - Generating from scratch')
		inputVectors = []
		countInputVectors = []
		outputLabels = []
		abstractVectorDict = abstractVectorDictList[0]
		countVectorDict = abstractVectorDictList[1]
		try:
			with open(RETRO_CITATION_FILE, 'rb') as f:
				retrospectiveCitations = pickle.load(f)
		except:
			retrospectiveCitations = getRetrospectiveCitations(pmidDict)
			with open(RETRO_CITATION_FILE, 'wb') as f:
				pickle.dump(retrospectiveCitations, f)

		print(retrospectiveCitations)
		print('hi')

		with open(CITATION_DICT_FILE, 'rb') as f:
			citedByDict = pickle.load(f)

		for x, y in pairList:
			# print paperDateDict.get(y, None)
			if len(abstractVectorDict[x]) == 0 or len(abstractVectorDict[y]) == 0: continue
			if x not in retrospectiveCitations or retrospectiveCitations.get(x, set([])) == None: continue
			else: xCitations = retrospectiveCitations.get(x, set([]))
			if y not in retrospectiveCitations or retrospectiveCitations.get(y, set([])) == None: continue
			else: yCitations = retrospectiveCitations.get(y, set([]))

			# start = time.time()
			# print(time.time() - start)
			featureVector = util.extractFeatures(
				abstractVectorDict[x],
				abstractVectorDict[y],
				paperAuthorDict[x],
				paperAuthorDict[y],
				xCitations,
				yCitations,
				util.dateDifference(paperDateDict.get(x, None), paperDateDict.get(y, None))
				)
			countFeatureVector = util.extractFeatures(
				countVectorDict[x],
				countVectorDict[y],
				paperAuthorDict[x],
				paperAuthorDict[y],
				xCitations,
				yCitations,
				util.dateDifference(paperDateDict.get(x, None), paperDateDict.get(y, None))
				)
			# print(time.time() - start)
			inputVectors.append(featureVector)
			countInputVectors.append(countFeatureVector)
			outputLabels.append(util.areCoCited(xCitations, yCitations))
			# print(time.time() - start)
		with open(INPUT_VECTORS_FILE, 'wb') as f:
			pickle.dump(inputVectors, f)
		with open(COUNT_INPUT_VECTORS_FILE, 'wb') as f:
			pickle.dump(countInputVectors, f)
		with open(OUTPUT_LABELS_FILE, 'wb') as f:
			pickle.dump(outputLabels, f)
	print('Created input and output vectors')
	# What I used for the 186 papers to get enough co-citations and fewer non-co-citations
	# newOutput = []
	# newInput = []
	# newCountInput = []
	# for i in xrange(len(outputLabels)):
	# 	if outputLabels[i] == True:
	# 		if i > 0:
	# 			newOutput.append(outputLabels[i-1])
	# 			newInput.append(inputVectors[i-1])
	# 			newCountInput.append(countInputVectors[i-1])
	# 		if i < len(outputLabels) - 1:
	# 			newOutput.append(outputLabels[i+1])
	# 			newInput.append(inputVectors[i+1])
	# 			newCountInput.append(countInputVectors[i+1])
	# 		newOutput.append(outputLabels[i])
	# 		newInput.append(inputVectors[i])
	# 		newCountInput.append(countInputVectors[i])
	# 		i+= 3
	# inputVectors = newInput
	# countInputVectors = newCountInput
	# outputLabels = newOutput

	# Turn into np arrays
	inputVectors = np.array(inputVectors)
	countInputVectors = np.array(countInputVectors)
	outputLabels = np.array(outputLabels)

	# Randomly arrange the training data
	np.random.seed(100)
	m, n = inputVectors.shape
	p = np.random.permutation(m)
	trainIndexEnd = int(numTraining * m)

	trainData = inputVectors[p,:]
	countTrainData = countInputVectors[p,:]
	trainLabels = outputLabels[p]

	testData = trainData[trainIndexEnd:,:]
	countTestData = countTrainData[trainIndexEnd:,:]
	testLabels = trainLabels[trainIndexEnd:]

	trainData = trainData[:trainIndexEnd,:]
	countTrainData = countTrainData[:trainIndexEnd,:]
	trainLabels = trainLabels[:trainIndexEnd]

	# # run logistic regression on these labels
	# print 'Logistic Regression'
	# try:
	# 	with open(LOG_REG_MODEL_FILE, 'rb') as f:
	# 		logreg = pickle.load(f)
	# 	with open(CONTROL_LOG_REG_MODEL_FILE, 'rb') as f:
	# 		controlLogreg = pickle.load(f)
	# except:
	# 	logreg = LogisticRegression().fit(trainData, trainLabels)
	# 	# run logistic regression on control
	# 	controlLogreg = LogisticRegression().fit(countTrainData, trainLabels)
	# 	with open(LOG_REG_MODEL_FILE, 'wb') as f:
	# 		pickle.dump(logreg, f)
	# 	with open(CONTROL_LOG_REG_MODEL_FILE, 'wb') as f:
	# 		pickle.dump(controlLogreg, f)
	# output = logreg.predict(testData)
	# controlOuput = controlLogreg.predict(countTestData)

	# Run MLP Classification
	print 'MLP Classification'
	try:
		with open(MLP_MODEL_FILE, 'rb') as f:
			mlp = pickle.load(f)
		with open(CONTROL_MLP_MODEL_FILE, 'rb') as f:
			controlmlp = pickle.load(f)
	except:
		mlp = MLPClassifier().fit(trainData, trainLabels)
		controlmlp = MLPClassifier().fit(countTrainData, trainLabels)
		with open(MLP_MODEL_FILE, 'wb') as f:
			pickle.dump(mlp, f)
		with open(CONTROL_MLP_MODEL_FILE, 'wb') as f:
			pickle.dump(controlmlp, f)
	output = mlp.predict(testData)
	controlOuput = controlmlp.predict(countTestData)

	print 'train labels ', trainLabels
	print 'output ', output
	print 'control output ', controlOuput
	print 'test labels ', testLabels

	print "-----Data Info-----"
	print "TF-IDF Train Matrix: ", trainData.shape
	print "Count Train Matrix: ", countTrainData.shape
	print "Test Data Matrix: ", testData.shape
	print "-----TF-IDF Vector-----"
	print "Accuracy Score: %f" %metrics.accuracy_score(testLabels, output)
	print "Precision: %f" %metrics.precision_score(testLabels, output)
	print "Recall: %f" %metrics.recall_score(testLabels, output)
	print "F1: %f" %metrics.f1_score(testLabels, output)
	print "Log Loss: %f" %metrics.log_loss(testLabels, output)

	print "-----Count Vector-----"
	print "Accuracy Score: %f" %metrics.accuracy_score(testLabels, controlOuput)
	print "Precision: %f" %metrics.precision_score(testLabels, controlOuput)
	print "Recall: %f" %metrics.recall_score(testLabels, controlOuput)
	print "F1: %f" %metrics.f1_score(testLabels, controlOuput)
	print "Log Loss: %f" %metrics.log_loss(testLabels, controlOuput)





main()
