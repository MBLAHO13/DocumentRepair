"""Document Repair
Uses the database of triples created by databaseConstructor and dbConnector to
predict words missing from input documents deliniated by user-chosen delimiter
The user is given a choice between outputting a table of likely words to the 
console or inserting the most likely word into a copy of the document.

Max Mattes, Karishma Changlani, Colleen Blaho
05/20/2014

Changelog located on GitHub: https://github.com/CBLAHO13/DocumentRepair/

Written for Python 2.7
"""
import sys
import dbConnector as db
import databaseConstructor as fileParser
import mysql.connector
from collections import deque

def userSelectOn() :
	"""Gives user a choce of repair modes
	Function Arguments
	None
	Function Returns
	bool: true if tables should be shown, false otherwise
	"""
	choice = ''
	while choice not in ['0','1','repair','list'] :
		choice = raw_input('Choose from the menu:\n[0] Repair\n[1] ' + \
			'List\n[2] Help\n>>> ').lower().strip()
		if choice in ['2','help'] :
			print '"Repair" will output a file with replacements ' + \
				'automatically chosen by the\nprogram. "List" will list ' + \
				'several possibilities to the console and the user\n' + \
				'chooses which word to insert'
	if choice in ['0','repair'] :
		return False
	else
		return True

def repair(doc, database) :
	"""Repairs a document using probabilities stored in the database
	Function Arguments
	doc: Document to be repaired
	database: Database with probaility tables
	Function Returns
	File output, but no function returns
	"""
	with open(doc.name + '~repaired','w') as fixedDoc :
		delim = raw_input('Enter a string to represent a missing word\n>>> ')
		wordQueue = deque('.'*5)
		for word in inputFile.read().replace('--',' ').split() :
			# Cleaning input
			word = word.lower().strip(' \t,;:()\'"[]')
			# Ignoring blanks
			if word == '' :
				continue
			if word[-1] in ['.','?','!'] :
				word = word.strip('.?!')
				endOfSentence = True
			fixedDoc.write(wordQueue.popleft())
			wordQueue.append(word)
			if wordQueue[2] == delim :
				replaceWord(wordQueue, database)
				wordQueue[2] = replaceWord(wordQueue, database)
			if endOfSentence :
				fixedDoc.write(wordQueue.popleft())
				wordQueue.append('.')
				if wordQueue[2] == delim :
					wordQueue[2] = replaceWord(wordQueue, database)
		while len(wordQueue) > 0 :
			fixedDoc.write(wordQueue.popleft())
			
def replaceWord(wordList, database)
	"""Replaces a missing word by probaility or by selection from probable list
	Function Arugments
	wordList: Queue of 5 words including missing word
	database: Database of probabilities to work with
	Function Return
	string: returns chosen string to replace missing word
	"""
	# TODO: this. This whole thing right here. Do this.

def main() :
	dbName = raw_input('Please enter a name for the database to be used\n>>> ')
	database = db.openPidb(dbName)
	fileParser.parseFiles('.txt','r','Please enter a .txt document to be ' + \
		'parsed and added to the database or\n"CONTINUE" to repair ' + \
		'documents or "EXIT" to quit\n>>> ',fileParser.fileToDatabase,database)
	fileParser.parseFiles('.txt','r','Please enter a .txt file to be ' + \
		'repaired or "EXIT" to quit\n>>> ',repair,database)
	database.close()
	return 0

if __name__ == '__main__' :
	sys.exit(main())