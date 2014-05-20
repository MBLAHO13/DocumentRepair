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
	
def openPidb() :
	"""Opens database on Raspberri Pi for use
	Function Arguments
	None
	Function Returns
	MySQLdb Connection Object
	"""
	db = mysql.connector.connect(user='remoteaccess',password=getPassword(),
		database='engr103',host=getIP())
	cursor = db.cursor()
	cursor.execute('SET collation_connection = \'utf8_general_ci\'')
	cursor.execute('ALTER DATABASE engr103 CHARACTER SET utf8 COLLATE utf8_general_ci')
	return db
	
def insert(base, word, isFirstFollowing, db) :
	"""Inserts a triple into the base table
	Function Arguments
	base: Base word, used as table name
	word: Word to insert into table
	isFirstFollowing: Flag. 1 if following, 0 if twice following
	db: Database to work with
	Function Return
	None
	"""
	cursor = db.cursor()
	try :
		cursor.execute('CREATE TABLE `' + base + '` ( `word` varchar(50), ' + \
			'`FirstFollowing` int NOT NULL DEFAULT 0, `SecondFollowing` ' + \
			'int NOT NULL DEFAULT 0, PRIMARY KEY (`word`));')
		cursor.execute('ALTER TABLE `' + base + '` CONVERT TO CHARACTER ' + \
			'SET utf8 COLLATE utf8_general_ci')
	except mysql.connector.Error as err :
		if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
			print 'Table already exists'
		else:
			print err.msg
	
	try :
		cursor.execute('INSERT INTO `' + base + '` (`word`,`FirstFollowing`,' + \
			'`SecondFollowing`) VALUES ("' + word + '",0,0);')
		print cursor.statement
		print 'Added row'
	except mysql.connector.IntegrityError as err :
		print 'Row already exists'
	
	cursor.execute('UPDATE `' + base + '` SET FirstFollowing = FirstFollowing + 1 WHERE STRCMP(`word`,"' + word + '") = 0')
	db.commit()
	cursor.close()
	
	'''
	cur = db.cursor();
	field=0;

	#Check if table exists, if it doesnt create the specified table.
	if not isTable(mainword,db):
		cur1.execute("Creat table _"+mainword+"(Word varchar(50), FirstFollowing int NOT null default 0, SecondFollowing int NOT NULL default 0)")
	
	cur1.execute("SELECT COUNT(*) FROM _"+mainword+" where Word=\""+word+"\"")

	for row in cur1.fetchall() :
		#data from rows
		 for i in range (0, len(row)) :
		  field = str(row[i]);
	
	if field!=0: 
		if isFirstFollowing:
			cur3.execute("UPDATE _"+mainword+" SET FirstFollowing=FirstFollowing+1 WHERE word=\""+word+"\"")
			print ("Update Statement Executed");
		else:
			cur3.execute("UPDATE _"+mainword+" SET SecondFollowing=SecondFollowing+1 WHERE word=\""+word+"\"")
			print ("Update Statement Executed");
	else:
		if isFirstFollowing:
			cur3.execute("INSERT into _"+mainword+" values(\""+word+"\", 1, 0)");
			print ("Insert Statement Executed");
		else:
			cur3.execute("INSERT into _"+mainword+" values(\""+word+"\", 0, 1)");
			print ("Insert Statement Executed");
	# close the cursor
	cur1.close();
	cur2.close();
	cur3.close();
	db.commit();
	'''