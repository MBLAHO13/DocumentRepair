"""Python to SQL connector
Interfaces between python and a remote SQL database and has functions to work
in conjunction with databaseConstructor and documentRepair for creating and
maintaining the database.

Uses mysql.connector from http://dev.mysql.com/doc/connector-python/en/index.html

Max Mattes, Karishma Changlani, Colleen Blaho
05/20/2014

Changelog located on GitHub: https://github.com/CBLAHO13/DocumentRepair/

Written for Python 2.7
"""

import sys
import urllib2
import mysql.connector
from mysql.connector import errorcode

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
	db = mysql.connector.connect(user='remoteaccess',password=getPassword(),
		host=getIP())
	cursor = db.cursor()
	try :
		cursor.execute('CREATE DATABASE `' + dbName + '`;')
		cursor.execute('SET collation_connection = \'utf8_general_ci\';')
		cursor.execute('ALTER DATABASE `' + dbName + '` CHARACTER SET utf8 COLLATE utf8_general_ci;')
	except mysql.connector.errors.DatabaseError :
		pass
	cursor.execute('USE `' + dbName + '`;')
	return db

def isTable(base, db) :
	"""
	Checks if a base table already exists in the database
	
	Args:
		base: Base word, used as table name
		db: Database of word counts
	Returns:
		False if table does not exist, True otherwise
	"""
	cursor = db.cursor();
	field=0;
	cursor.execute('SELECT COUNT(*)FROM information_schema.tables WHERE table_schema = "' + str(db.database) + '" AND table_name = "'+base+'"' )
	for row in cursor.fetchall():
		field = row[0];
	cursor.close();
	if field == 0 :
		return False;
	else:
		return True;
	
def isRow(base, word, db):
	cursor=db.cursor()
	field=0;
	cursor.execute('SELECT COUNT(*) FROM `'+base+'` where Word="'+word+'"')

	for row in cursor.fetchall() :
		field = row[0];
	if field==0:
		return False;
	else:
		return True;
	
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
	
	# Creates table if it does not already exist
	if not isTable(base, db):
		cursor.execute('CREATE TABLE `' + base + '` ( `word` varchar(50), ' + \
			'`FirstFollowing` int NOT NULL DEFAULT 0, `SecondFollowing` ' + \
			'int NOT NULL DEFAULT 0, PRIMARY KEY (`word`));')
	
	'''Attempts to create a new row for fol. If it fails, that means the row 
	already exists and it moves on'''
	try :
		cursor.execute('INSERT INTO `' + base + '` (`word`,`FirstFollowing`' +\
			',`SecondFollowing`) VALUES ("' + fol + '",0,0);')
	except mysql.connector.IntegrityError as err :
		pass
	
	'''Increments 'fol' row for following count'''
	cursor.execute('UPDATE `' + base + '` SET FirstFollowing = ' + \
		'FirstFollowing + 1 WHERE STRCMP(`word`,"' + fol + '") = 0;')
		
	'''Attempts to create a new row for twiceFol. If it fails, that means the
	row already exists and it moves on'''
	try :
		cursor.execute('INSERT INTO `' + base + '` (`word`,`FirstFollowing`' +\
			',`SecondFollowing`) VALUES ("' + twiceFol + '",0,0);')
	except mysql.connector.IntegrityError as err :
		pass
	
	'''Increments row for following or twice following count'''
	cursor.execute('UPDATE `' + base + '` SET SecondFollowing = ' + \
		'SecondFollowing + 1 WHERE STRCMP(`word`,"' + twiceFol + '") = 0;')
	
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
