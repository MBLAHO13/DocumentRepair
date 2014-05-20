import sys
import dataConnectionFunctions as db

def parseUserFile(parseFunc,fileType,inputMessage) :
	'''
	Requests user input for filename and attepts to open file and parse based
	on given parsing function. 'parseFunc' is the parsing function which
	accepts a file object as input and 'fileType' is the chosen filetype to be 
	parsed as a string of the extension. Example: '.txt'
	inputMessage is the message to be shown to the user requesting a filename.
	Function will continue processing documents until the user exits.
	'''
	userInput = ''
	while userInput != 'EXIT' :
		userInput = raw_input(inputMessage)
		if userInput.endswith(fileType) :
			try :
				userFile = open(userInput, 'r')
			except IOError :
				print 'Failed to open file. Check to make sure it is in the ' + \
					'current working directory'
			else :
				parseFunc(userFile)
		elif userInput != 'EXIT' :
			print 'Incorrect file extension'

def fileToDatabase(inputFile) :
	'''
	Takes a file object and inserts word triplets into the database after
	parsing and cleaning the input. Throws IOError if file not opened for
	reading.
	'''
	current = fol = folFol = '.'
	i = 0
	# Splitting into words
	for word in inputFile.read().replace('--',' ').split() :
		# Cleaning input
		word = word.lower().strip(' \t,;:()\'"[]')
		# Ignoring blanks
		if word == '' :
			continue
		current,fol,folFol = fol,folFol,word
		if not (current == '.' and fol == '.') :
			print current, ':', fol, ':', folFol
			# db.insert(current,fol,1)
			# db.insert(current,folFol,0)
			i += 1
		if i > 200 : # Limiter for testing purposes, please ignore
			break
		
				
def main() :
	'''
	Accepts user input files using console and parses the words into the
	database defined in dataConnectionFunctions. Words are collected and
	counted to produce probabilities to be used later by the document
	repair module.
	'''
	parseUserFile(fileToDatabase,'.txt','Please enter a .txt document to ' + \
			' be parsed and added to the database or "EXIT"\nto quit\n>>> ')
	return 0

if __name__ == '__main__' :
	sys.exit(main())