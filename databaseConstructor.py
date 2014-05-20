import sys
import dataConnectionFunctions as db

def parseUserFile(parseFunc,fileType) :
	'''
	Requests user input for filename and attepts to open file and parse based
	on given parsing function. 'parseFunc' is the parsing function which
	accepts a file object as input and 'fileType' is the chosen filetype to be 
	parsed as a string of the extension. Example: '.txt'
	'''
	userInput = ''
	while userInput != 'EXIT' :
		userInput = raw_input('Please enter a ' fileType ' document to be \
			parsed and added to the database or "EXIT"\nto quit\n>>> ')
		if userInput.endswith(fileType) :
			try :
				userFile = open(userInput, 'r')
			except IOError :
				print 'Failed to open file. Check to make sure it is in the \
					current working directory'
			else :
				parseFunc(userFile)

def fileToDatabase(inputFile) :
	'''
	Takes a file object and inserts word triplets into the database after
	parsing and cleaning the input. Throws IOError if file not opened for
	reading.
	'''
	current,fol,folFol = '.'
	for word in inputFile.read().split() :
		current,fol,folFol = fol,folFol,word
		if not (current == '.' and fol == '.') :
			db.insert(current,fol,1)
			db.insert(current,folFol,0)
		
				
def main() :
	'''
	Accepts user input files using console and parses the words into the
	database defined in dataConnectionFunctions. Words are collected and
	counted to produce probabilities to be used later by the document
	repair module.
	'''
	parseUserFile(fileToDatabase,'.txt')	
	return 0

if __name__ == '__main__' :
	sys.exit(main())