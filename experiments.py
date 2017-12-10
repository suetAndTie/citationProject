from dataGeneration import generateDataAndLabels

def main():
	matrix, labels = generateDataAndLabels(['copd_tiny.txt'], 'labels.pickle')
	print(matrix, labels)

if __name__ == "__main__":
	main()