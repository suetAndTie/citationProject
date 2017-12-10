from dataGeneration import generateDataAndLabels
import numpy as np
import os.path
import constants
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as metrics


# Types of machine learning models to use
MODELS = {
'logreg':LogisticRegression,
'svc':SVC,
'mlp':MLPClassifier
}


# Rearranges the data and then returns the train (60), dev (20), and test (20) sets
def getDataSets(matrix, controlMatrix, labels):
	# Randomly rearranges data according the the np random seed
	np.random.seed(100)
	m, n = matrix.shape
	p = np.random.permutation(m)
	matrix = matrix[p,:]
	controlMatrix = controlMatrix[p,:]
	labels = labels[p]
	# End index for the train and dev sets
	trainEndIdx = int(constants.PERCENT_TRAIN * m)
	devEndIdx = trainEndIdx + int(constants.PERCENT_DEV * m)

	# Each data set tuple has input matrix, control input matrix, and labels
	trainData = (matrix[:trainEndIdx, :], controlMatrix[:trainEndIdx, :], labels[:trainEndIdx])
	devData = (matrix[trainEndIdx:devEndIdx, :], controlMatrix[trainEndIdx:devEndIdx, :], labels[trainEndIdx:devEndIdx])
	testData = (matrix[devEndIdx:, :], controlMatrix[devEndIdx:, :], labels[devEndIdx:])

	return trainData, devData, testData


# Runs the classification model on the data and gets back the model and control model
# Also saves the model
def runModel(modelName, trainData, devData, testData):
	fileName = 'models' + modelName + '.pickle'
	if os.path.isfile(fileName):
		with open(fileName, 'rb') as f:
			model, controlModel = pickle.load(f)
	else:
		modelFunction = MODELS[modelName]
		model = modelFunction().fit(trainData[0], trainData[2])
		controlModel = modelFunction().fit(trainData[1], trainData[2])
		with open(fileName, 'wb') as f:
			pickle.dump((model, controlModel), f)

	trainOutput = model.predict(trainData[0])
	trainControlOutput = model.predict(trainData[1])
	devOutput = model.predict(devData[0])
	devControlOutput = controlModel.predict(devData[1])
	testOutput = model.predict(testData[0])
	testControlOutput = controlModel.predict(testData[1])
	print '-----Training Set-----'
	print '---TF-IDF---'
	getMetrics(trainOutput, trainData[2])
	print '---Control---'
	getMetrics(trainControlOutput, trainData[2])
	print '-----Dev Set-----'
	print '---TF-IDF---'
	getMetrics(devOutput, devData[2])
	print '---Control---'
	getMetrics(devControlOutput, devData[2])
	print '-----Test Set-----'
	print '---TF-IDF---'
	getMetrics(testOutput, testData[2])
	print '---Control---'
	getMetrics(testControlOutput, testData[2])
	print '\n\n'


# Computes classification metrics of the output based on labels
def getMetrics(output, labels):
	print 'Accuracy Score: %f' %metrics.accuracy_score(labels, output)
	print 'Precision: %f' %metrics.precision_score(labels, output)
	print 'Recall: %f' %metrics.recall_score(labels, output)
	print 'F1: %f' %metrics.f1_score(labels, output)
	print 'Log Loss: %f' %metrics.log_loss(labels, output)


def main():
	topic = constants.TOPIC
	matrix, controlMatrix, labels = generateDataAndLabels(constants.DATA_FILES, topic+'Matrix.pickle', topic+'CountMatrix.pickle', topic+'Labels.pickle')
	print(matrix, controlMatrix, labels)
	trainData, devData, testData = getDataSets(matrix, controlMatrix, labels)
	print '-----Data Info-----'
	print 'Train Matrix: ', trainData[0].shape
	print 'Dev Matrix: ', devData[0].shape
	print 'Test Data Matrix: ', testData[0].shape
	print '\n\n'
	for modelName in MODELS:
		print '----------' + modelName + '----------'
		runModel(modelName, trainData, devData, testData)



if __name__ == "__main__":
	main()
