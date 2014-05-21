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
	"""Pulls IP down from webaddress published by the Raspberry Pi
	Function Arguments
	None
	Function Returns
	IP address as string
	"""
	page = urllib2.urlopen('http://www.cs.drexel.edu/~cpb49/ipaddress')
	ip = page.read().strip()
	page.close()
	return ip

def getPassword() :
	"""Acquires password from local file to prevent accidentally leaking
	the password out to the internet
	Function Arguments
	None
	Function Returns
	Password as string
	"""
	with open('password.txt','r') as file :
		pw = file.read().strip()
	return pw
	
def openPidb(dbName) :
	"""Opens database on Raspberri Pi for use
	Function Arguments
	dbName: Name of the database to be created
	Function Returns
	MySQLdb Connection Object
	"""
	db = mysql.connector.connect(user='remoteaccess',password=getPassword(),
		host=getIP())
	cursor = db.cursor()
	try :
		cursor.execute('CREATE DATABASE `' + dbName + '`;')
	except mysql.connector.errors.DatabaseError :
		pass
	cursor.execute('USE `' + dbName + '`;')
	cursor.execute('SET collation_connection = \'utf8_general_ci\';')
	cursor.execute('ALTER DATABASE `' + dbName + '` CHARACTER SET utf8 COLLATE utf8_general_ci;')
		
	return db
	
def insert(base, fol, twiceFol, db) :
	"""Inserts a triple into the base table
	Function Arguments
	base: Base word, used as table name
	fol: Following word
	twiceFol: Twice Following word
	db: Database to work with
	Function Return
	None
	"""
	cursor = db.cursor()
	
	'''Attempts to create the table. If it fails, that means the table already
	exists and it moves on'''
	try :
		cursor.execute('CREATE TABLE `' + base + '` ( `word` varchar(50), ' + \
			'`FirstFollowing` int NOT NULL DEFAULT 0, `SecondFollowing` ' + \
			'int NOT NULL DEFAULT 0, PRIMARY KEY (`word`));')
		cursor.execute('ALTER TABLE `' + base + '` CONVERT TO CHARACTER ' + \
			'SET utf8 COLLATE utf8_general_ci;')
	except mysql.connector.Error as err :
		if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
			pass
		else:
			print err.msg
	
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
	"""Chooses one column in base table and converts to dict with words as keys
	Function Arguments
	base: Base word, used as table name
	order: Following, Twice Following, etc. int to show distance from base
	db: Database to work with
	"""
	cursor = db.cursor()
	wordMap = {}
	cursor.execute('DESCRIBE `' + base + '`;')
	i = 0
	for item in cursor :
		if i == order :
			column = str(item[0])
		i += 1
	cursor.execute('SELECT `word`,`' + column + '` FROM `' + base + '`;')
	for (word, count) in cursor :
		if count > 0 :
			wordMap[word] = count
	cursor.close()
	return wordMap