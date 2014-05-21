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

def parseFiles(fileExt, mode, inputMessage, parseFunc, *args) :
	"""Continually requests user input files and processes with parseFunc
	Function Arguments
	fileExt: Extension for file to be parsed
	mode: Python-defined modes for opening a file (r,w,rw,...)
	inputMessage: Message shown to user requesting file names for processing
	parseFunc: Function to be run on opened files. Must accept file object as
	input.
	*args: Arguments to be pased to parseFunc after the file object.
	Function Returns
	None
	"""
	userInput = ''
	while userInput not in ('EXIT','CONTINUE') :
		userInput = raw_input(inputMessage)
		if userInput.endswith(fileExt) :
			try :
				 with open(userInput,mode) as userFile :
					parseFunc(userFile,*args)
			except IOError :
				print 'Failed to open file correctly. Check to make sure ' + \
					'it is in the current working directory'
		elif userInput not in ('EXIT','CONTINUE') :
			print 'Incorrect file extension'

def fileToDatabase(inputFile, database) :
	"""Builds database of word triplets from file object
	Function Arguments
	inputFile: File object to read from
	database: Database to add to (in the form of a MySQLdb Connection Object)
	Function Returns
	None
	"""
	current = fol = twiceFol = '.'
	# Splitting into words
	i = 0
	print 'Inserting words from ' + inputFile.name + '...'
	for word in inputFile.read().replace('--',' ').split() :
		# Cleaning input
		word = word.lower().strip(' \t,;:()\'"[]')
		# Ignoring blanks
		if word == '' :
			continue
			
		# Establishing punctuation as separate 'word' in database
		if word[-1] in ['.','?','!'] :
			word = word.strip('.?!')
			current,fol,twiceFol,word = fol,twiceFol,word,'.' # Shifting buffer
			db.insert(current,fol,twiceFol,database)
			
		# Moving buffer and adding to database
		current,fol,twiceFol = fol,twiceFol,word
		if not (current == '.' and fol == '.') :
			db.insert(current,fol,twiceFol,database)
		i += 1
		if i > 200 :
			break
				
def main() :
	"""Runs fileToDatabase in parseFiles to create a database from .txt files
	"""
	probabilitydb = db.openPidb('testDB')
	parseFiles('.txt','r','Please enter a .txt document to be parsed and ' + \
		'added to the database or "EXIT"\nto quit\n>>> ',fileToDatabase,
		probabilitydb)
	probabilitydb.close()
	return 0

if __name__ == '__main__' :
	sys.exit(main())