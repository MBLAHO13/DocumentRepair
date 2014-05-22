"""
Document Repair
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
import databaseConstructor as fparser
import mysql.connector
from collections import deque

def userSelectOn() :
	"""
	Give user a choce of repair modes
	
	Args:
		None
	Returns:
		True if tables should be shown, false otherwise
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
	else :
		return True

def repair(doc, database) :
	"""
	Repair a document using probabilities stored in the database
	
	Args:
		doc: Document to be repaired
		database: Database of word counts
	Returns:
		File output, but no function returns
	"""
	userSelect = userSelectOn()
	with open(doc.name + '~repaired','w') as fixedDoc :
		delim = '...#' # raw_input('Enter a string to represent a missing word\n>>> ')
		wordQueue = deque('.'*5)
		endOfSentence = False
		for word in doc.read().replace('--',' ').split() :
			# Cleaning input
			word = word.lower().strip(' \t,;:()\'"[]')
			# Ignoring blanks
			if word == '' :
				continue
			if word[-1] in ['.','?','!'] and len(word) > 0 :
				word = word.strip('.?!')
				endOfSentence = True
			fixedDoc.write(wordQueue.popleft() + ' ')
			wordQueue.append(word)
			if wordQueue[2] == delim :
				replaceWord(wordQueue, database, userSelect)
				wordQueue[2] = replaceWord(wordQueue, database, userSelect)
			if endOfSentence :
				fixedDoc.write(wordQueue.popleft() + ' ')
				wordQueue.append('.')
				if wordQueue[2] == delim :
					wordQueue[2] = replaceWord(wordQueue, database, userSelect)
				endOfSentence = False
		while len(wordQueue) > 0 :
			fixedDoc.write(wordQueue.popleft())
			
def replaceWord(wordList, database, userSelect) :
	"""
	Replace a missing word by probaility or by selection from probable list
	
	Args:
		wordList: Queue of 5 words including missing word
		database: Database of word counts
	Returns:
		string: returns chosen string to replace missing word
	"""
	probableTable = getLeftProbability(wordList,database)
	probableTable = getRightProbability(wordList,probableTable,database)
	sortedProbabilities = zip(probableTable.values(),probableTable.keys())
	sortedProbabilities.sort()
	sortedProbabilities.reverse()
	chosenWord = str(sortedProbabilities[0][1])
	if userSelect :
		print 'Word:'.ljust(15),'Probability:'.ljust(15)
		listLimiter = 30;
		for word in sortedProbabilities :
			print word[1].ljust(15), (str(word[0]*float(25)) + '%').ljust(15)
			listLimiter = listLimiter-1
			if listLimiter <= 0 :
				break
		print 'Context:',
		for word in wordList :
			print word,
		print # newline
		chosenWord = raw_input('Select a word from the list or input your ' + \
			 'own to replace missing word\n>>> ')
	return chosenWord
		
def getLeftProbability(wordList, database) :
	"""
	Get probability table summed from two words left of missing word
	
	Args:
		wordList: 2-word deque of words left of missing word
		database: Database of word counts
	Returns:
		Dict of word,probability pairs (where probability is the summed counts
			from the two words in wordList)
	"""
	firstDict = db.getDict(wordList[0],2,database)
	secondDict = db.getDict(wordList[1],1,database)
	probableDict = {}
	for word in firstDict :
		probableDict[word] = firstDict[word]
	for word in secondDict :
		if word in probableDict :
			probableDict[word] += secondDict[word]
		else :
			probableDict[word] = secondDict[word]
	return probableDict
	
def getRightProbability(wordList,probableTable,database) :
	"""
	Add to probability table based on probabilities of words right of the
		missing word
		
	Args:
		wordList: 2-word deque of words right of missing word
		probableTable: dict of word,count pairs from getLeftProbability()
		database: Database of word counts
	Returns:
		Dict of word,probability pairs (where probability is the summed counts
			from both words behind and in front of the missing word)
	"""
	for word in probableTable :
		firstDict = db.getRow(word,wordList[3],1,database)
		secondDict = db.getRow(word,wordList[4],2,database)
		if wordList[3] in firstDict :
			probableTable[word] += firstDict[wordList[3]]
		if wordList[4] in secondDict :
			probableTable[word] += secondDict[wordList[4]]
	return probableTable

def main() :
	"""
	Create a database of word counts and probabilistically repair documents
	
	Args:
		None
	Returns:
		int 0
		Potential database creation and file output based on user selections
	"""
	dbName = raw_input('Please enter a name for the database to be used\n>>> ')
	database = db.openPidb(dbName)
	exit = fparser.parseFiles('.txt',['EXIT','CONTINUE'],'Please enter a .txt document to be ' + \
		'parsed and added to the database or\n"CONTINUE" to repair ' + \
		'documents\n>>> ',fparser.fileToDatabase,database)
	if not exit :
		fparser.parseFiles('.txt',['EXIT'],'Please enter a .txt file to be ' + \
			'repaired or "EXIT" to quit\n>>> ',repair,database)
	database.close()
	return 0

if __name__ == '__main__' :
	sys.exit(main())
