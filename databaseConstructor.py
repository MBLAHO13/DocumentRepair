"""Database constructor
Builds a database of word counts from input .txt files. The database is built
using dataConnectionFunctions.py and consists of a series of tables labeled by
their base word and containing three columns: a list of words, the number of
times that word occurred immediately following the base word, and the number of
times it occurred as the word after that. For example, in the sentence "Dogs
are animals", "are" is immediately following "Dogs" and "animals" is the word
after that, referred to internally as "twice following"

Max Mattes, Karishma Changlani, Colleen Blaho
05/20/2014

Changelog located on GitHub: https://github.com/CBLAHO13/DocumentRepair/

Written for Python 2.7
"""
import sys
import dbConnector as db
import mysql.connector
from collections import deque

def parseFiles(fileExt, exitList, inputMessage, parseFunc, *args) :
	"""
	Continually request user input files and process with parseFunc
	
	Args:
		fileExt: Extension for file to be parsed
		exitList: List of strings the user can terminate the program with.
			exitList[0] is always the exit string.
		inputMessage: Message shown to user requesting file names for 
			processing
		parseFunc: Function to be run on opened files. Must accept file object
			as input.
		*args: Arguments to be pased to parseFunc after the file object.
	Returns:
	   BOOL true or false.
		True: The user wants to quit.
		False: The user wants to continue. 	
	"""
	userInput = ''
	while userInput not in exitList :
		userInput = raw_input(inputMessage)
		if userInput.endswith(fileExt) :
			try :
				 with open(userInput,'r') as userFile :
					parseFunc(userFile,*args)
			except IOError :
				print 'Failed to open file correctly. Check to make sure ' + \
					'it is in the current working directory'
		elif userInput == exitList[0] :
			return True
		elif userInput not in ('EXIT','CONTINUE') :
			print 'Incorrect file extension'
	return False

def fileToDatabase(inputFile, database) :
	"""
	Build database of word triplets from file object
	
	Args:
		inputFile: File object to read from
		database: Database of word counts
	Returns:
		None
	"""
	wordQueue = deque('.'*3)
	# Splitting into words
	print 'Inserting words from ' + inputFile.name + '...'
	numAdded = 0
	for word in inputFile.read().replace('--',' ').split() :
		# Cleaning input
		word = word.lower().strip(' \t,;:()\'"[]')
		# Ignoring blanks
		if word == '' :
			continue
			
		# Establishing punctuation as separate 'word' in database
		if word[-1] in ['.','?','!'] and len(word) > 1:
			word = word.strip('.?!')
			# Shifting buffer
			wordQueue.popleft()
			wordQueue.append(word)
			word = '.'
			db.insert(wordQueue[0],wordQueue[1],wordQueue[2],database)
			numAdded += 2
			
		# Moving buffer and adding to database
		wordQueue.popleft()
		wordQueue.append(word)
		if not (wordQueue[0] == '.' and wordQueue[1] == '.') :
			db.insert(wordQueue[0],wordQueue[1],wordQueue[2],database)
			numAdded += 2
		if (numAdded % 100) == 0 :
			print 'Words added: ', numAdded
				
def main() :
	"""
	Create a database of word counts in triplets from .txt files
	
	Args:
		None
	Returns:
		int 0
	"""
	exitList = [ 'EXIT', 'CONTINUE' ]
	probabilitydb = db.openPidb('testDB')
	parseFiles('.txt',exitList,'Please enter a .txt document to be parsed and ' + \
		'added to the database or "EXIT"\nto quit\n>>> ',fileToDatabase,
		probabilitydb)
	probabilitydb.close()
	return 0

if __name__ == '__main__' :
	sys.exit(main())
