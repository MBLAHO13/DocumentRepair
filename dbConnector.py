"""Python to SQL connector
Interfaces between python and a remote SQL database and has functions to work
in conjunction with databaseConstructor and documentRepair for creating and
maintaining the database.

mysql.connector from http://dev.mysql.com/doc/connector-python/en/index.html

Max Mattes, Karishma Changlani, Colleen Blaho
05/20/2014

Changelog located on GitHub: https://github.com/CBLAHO13/DocumentRepair/

Written for Python 2.7
"""

import sys
import urllib2
import mysql.connector
from mysql.connector import errorcode

tableList = []
def getIP() :
	"""
	Pull IP down from webaddress published by the Raspberry Pi
	
	Args:
		None
	Returns:
		IP address as string
	"""
	page = urllib2.urlopen('http://www.cs.drexel.edu/~cpb49/ipaddress')
	ip = page.read().strip()
	page.close()
	return ip

def getPassword() :
	"""
	Acquire password from local file to prevent accidentally leaking the 
		password out to the internet
	
	Args:
		None
	Returns:
		Password as string
	"""
	with open('password.txt','r') as file :
		pw = file.read().strip()
	return pw
	
def openPidb(dbName) :
	"""
	Open database on Raspberri Pi for use
	
	Args:
		dbName: Name of the database to be created
	Returns:
		MySQLdb Connection Object
	"""
	print "Setting up database, please wait."
	db = mysql.connector.connect(user='remoteaccess',password=getPassword(),
		host=getIP())
	cursor = db.cursor()
	try :
		cursor.execute('CREATE DATABASE `' + dbName + '`;')
	except mysql.connector.errors.DatabaseError :
		pass
	cursor.execute('ALTER DATABASE `' + dbName + '` CHARACTER SET utf8 ' + \
		'COLLATE utf8_general_ci;')
	cursor.execute('SET collation_connection = \'utf8_general_ci\';')
	cursor.execute('USE `' + dbName + '`;')
	cursor.execute("SHOW TABLES")
	global tableList
	for table_name in cursor:
		tableList.append(table_name[0])	
	return db


def isTable(base, db) :
	"""
	Check if a base table already exists in the database
	
	Args:
		base: Base word, used as table name
		db: Database of word counts
	Returns:
		False if table does not exist, True otherwise
	"""
	tableExists = False
	
	if unicode(base, "utf-8") in tableList: #check our bookeeping list
		return True
	cursor = db.cursor()
	cursor.execute('SELECT COUNT(*)FROM information_schema.tables WHERE ' + \
		'table_schema = "' + str(db.database) + '" AND table_name = "' + \
		base + '"' )
	for row in cursor :
		tableExists = row[0]
	cursor.close()
	return tableExists
	
def isRow(base, word, db) :
	"""
	Check if a word already exists in the base table
	
	Args:
		base: Base word, used as table name
		word: Word row to be searched for
		db: Database of word counts
	Returns:
		False if row does not exist, True otherwise
	"""
	cursor = db.cursor()
	rowExists = False
	cursor.execute('SELECT COUNT(*) FROM `' + base + '` where `word`="' + \
		word + '"')
	for row in cursor :
		rowExists = row[0]
	cursor.close()
	return rowExists
	
def insert(base, fol, twiceFol, db) :
	"""
	Insert a triple into the base table
	
	Args:
		base: Base word, used as table name
		fol: Following word
		twiceFol: Twice Following word
		db: Database of word counts
	Returns:
		None
	"""
	cursor = db.cursor()
	global tableList
	# Creates table if it does not already exist
	if not isTable(base, db):
		cursor.execute('CREATE TABLE `' + base + '` ( `word` varchar(50), ' + \
			'`FirstFollowing` int NOT NULL DEFAULT 0, `SecondFollowing` ' + \
			'int NOT NULL DEFAULT 0, PRIMARY KEY (`word`));')
		tableList.append(base) #keep track of our additions
	#lock the tables. This is not a a transactional database, so this fluches the input buffer once.
	#According to documentation at http://dev.mysql.com/doc/refman/5.0/en/insert-speed.html It should
	# speed things up by 40%.
	cursor.execute('LOCK TABLES `' + base + '` WRITE;') 
	if not isRow(base, fol, db) :
		cursor.execute('INSERT INTO `' + base + '` (`word`,`FirstFollowing`' +\
			',`SecondFollowing`) VALUES ("' + fol + '",0,0);')
			
	cursor.execute('UPDATE `' + base + '` SET FirstFollowing = ' + \
		'FirstFollowing + 1 WHERE STRCMP(`word`,"' + fol + '") = 0;')
		
	if not isRow(base, twiceFol, db) :
		cursor.execute('INSERT INTO `' + base + '` (`word`,`FirstFollowing`' +\
			',`SecondFollowing`) VALUES ("' + twiceFol + '",0,0);')
	
	cursor.execute('UPDATE `' + base + '` SET SecondFollowing = ' + \
		'SecondFollowing + 1 WHERE STRCMP(`word`,"' + twiceFol + '") = 0;')
	cursor.execute('UNLOCK TABLES;') #unlock that for other people
	db.commit()
	cursor.close()
	
def getDict(base, order, db) :
	"""
	Choose one column in base table and return as dict with words as keys
	
	Args:
		base: Base word, used as table name
		order: Following, Twice Following, etc. int to show distance from base
		db: Database of word counts
	Returns:
		Dict of word,count pairs
	"""
	cursor = db.cursor()
	wordMap = {}
	try :
		cursor.execute('DESCRIBE `' + base + '`;')
	except mysql.connector.errors.ProgrammingError :
		pass
	else :
		i = 0
		for item in cursor :
			if i == order :
				column = str(item[0])
			i += 1
		totalCount = getTotal(base, column, db)
		cursor.execute('SELECT `word`,`' + column + '` FROM `' + base + '`;')
		for (word, count) in cursor :
			if count > 0 :
				wordMap[word] = float(count)/float(totalCount)
	finally :
		cursor.close()
		return wordMap
		
def getRow(base, word, order, db) :
	"""
	Choose one word in base table and return as dict with count as value
	
	Args:
		base: Base word, used as table name
		word: Word to be returned from the table
		order: Following, Twice Following, etc. int to show distance from base
		db: Database of word counts
	Returns:
		1-item dict of word,count pairs
	"""
	cursor = db.cursor()
	wordMap = {}
	try :
		cursor.execute('DESCRIBE `' + base + '`;')
	except mysql.connector.errors.ProgrammingError :
		pass
	else :
		i = 0
		for item in cursor :
			if i == order :
				column = str(item[0])
			i += 1
		totalCount = getTotal(base, column, db)
		cursor.execute('SELECT `word`,`' + column + '` FROM `' + base + \
			'` WHERE STRCMP(`word`,"' + word + '") = 0;')
		for (word, count) in cursor :
			if count > 0 :
				wordMap[word] = float(count)/float(totalCount)
	finally :
		cursor.close()
		return wordMap
	
def getTotal(base, column, db) :
	"""
	Sum a column in the table
	
	Args:
		base: Base word, used as table name
		column: Name of column
		db: Database of word counts
	Returns:
		Sum of column as int
	"""
	cursor = db.cursor()
	cursor.execute('SELECT SUM(`' + column + '`) FROM `' + base + '`;')
	for word in cursor :
		total = word[0]
	cursor.close()
	return total
