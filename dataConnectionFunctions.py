"""Python to SQL connector
Interfaces between python and a remote SQL database and has functions to work
in conjunction with databaseConstructor and documentRepair for creating and
maintaining the database.

Max Mattes, Karishma Changlani, Colleen Blaho
05/20/2014

Changelog located on GitHub: https://github.com/CBLAHO13/DocumentRepair/

Written for Python 2.7
"""

import sys
import urllib2
import socket
import MySQLdb # Connector Library

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
	ip = getIP()
	password = getPassword()
	return MySQLdb.connect(ip,'remoteaccess',password,'engr103')

def select(word,db) :
	"""Prints the base word's table from the database
	Function Arguments
	word: Base word chosen to print out
	db: Database to pull word from (in the form of a MySQLdb Connection Object)
	Function Returns
	None
	"""
	cur = db.cursor();
	cur.execute("SELECT * FROM _" + word);
	for row in cur.fetchall() :
		print field in row
	'''	for i in range (0, len(row)) :
			field = str(row[i]);
			print (field);'''
	cur.close();

#Checks if a table exists, returns true if it doesnt and
#returns false if it does.
def isTable(word,db):
	"""Checks the existence of a table in the database
	Function Arguments
	word: Base word table to be searched for
	db: Database to be searched
	Function Returns
	Returns true if table exists, false otherwise.
	"""
	cur = db.cursor();
	count = 0;
	cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'engr103' AND table_name = '_"+word+"'")
	for row in cur.fetchall() :
		for field in row :
			count = field[i];
	cur.close();
	if count == 0:
		return False;
	else:
		return True;
	
#Insert function for a table of mainword with  
def insert( mainword, word, isFirstFollowing, db):

	#create mutiple cursors to prevent overlapping queries
	cur1 = db.cursor();
	cur2 = db.cursor();
	cur3 = db.cursor();
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
	cur4.close();
	db.commit();

#Return the total of the FirstFollowing or the SecondFollowing
#Depending on the parameters
def total(word, isFirstFollowing):

	#create a cursor for the select
	cur = db.cursor();
	if isFirstFollowing:
		#execute an sql query
		cur.execute("SELECT SUM(FirstFollowing) FROM _"+word);

		##Iterate 
		for row in cur.fetchall() :
			#data from rows
			for i in range (0, len(row)) :
			  field = str(row[i]);
	else:
		#execute an sql query
		cur.execute("SELECT SUM(SecondFollowing) FROM _"+word);

		##Iterate 
		for row in cur.fetchall() :
			#data from rows
			for i in range (0, len(row)) :
			  field = str(row[i]);
 
	# close the cursor
	cur.close();
	field=int(field)
	return field;

#Makes a dictionary of words and percentages in a desired table
#Percentages can be of FirstFollowing or SecondFollowing depending
#on the boolean parameter isFirstFollowing
def listWords(word, isFirstFollowing):
	cur=db.cursor();
	d=dict();
	#execute an sql query
	cur.execute("SELECT * FROM _"+word);

	##Iterate
	if isFirstFollowing:
		for row in cur.fetchall() :
		#data from rows
			percentage=row[1]/total(word, isFirstFollowing)
			d[row[0]]=percentage;
	else:
		for row in cur.fetchall() :
		#data from rows
			percentage=row[2]/total(word, isFirstFollowing)
			d[row[0]]=percentage;

	#close the cursor
	cur.close();
	return d;
	
#delete a row of a value word. If no word is specified it sends
#out a prompt to drop the entire table and on users permission drops
#it.
def delete(mainword, word=""):

	#create a cursor for the select
	cur = db.cursor();

	if not isTable(mainword):
		print("Table _"+mainword+" doesn't exist")
	
	#check for the default value of word
	if (word==""):
		confirmation=raw_input("Are you sure you wish to completely drop this table. Enter Y/y to confirm \n")
		if confirmation=="Y" or confirmation=="y":
			cur.execute("DROP TABLE _"+mainword)
		else:
			print("please try again with a proper word input")
			return
	else:
		cur.execute("DELETE FROM _"+mainword+" where word=\""+word+"\"")
		print ("Delete Statement Executed");

		#Iterate 
		for row in cur.fetchall() :
			#data from rows
			 for i in range (0, len(row)) :
			  field = str(row[i]);

			#print 
			  print (field);

	#close the cursor
	cur.close();

	db.commit();
