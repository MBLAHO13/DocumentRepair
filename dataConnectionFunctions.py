import sys
import urllib2
import socket
#Connector Library
import MySQLdb

def opendb() :
	# getting our ipaddress
	page=urllib2.urlopen('http://www.cs.drexel.edu/~cpb49/ipaddress')
	ipaddress=page.read()
	ipaddress=ipaddress.rstrip()
	page.close()

	#getting our password
	'''
	piPassword replaces the password in plaintext. DO NOT SUBSTITUTE THE
	PASSWORD INTO THIS FILE! 
	'''
	file=open('password.txt', 'r')
	piPassword=file.read()
	piPassword=piPassword.rstrip()
	file.close()
	
	#Connecting to the database
	#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#s.connect(("gmail.com",80))
	#print(s.getsockname()[0])
	#s.close()
	#Needs to be changed in order to connect to the raspberry pi
	db = MySQLdb.connect(host=ipaddress, user="remoteuser", passwd=piPassword, db="engr103");
	#Execute and test the functions here.
	delete("and")
	
	#close the connection
	db.close ();

	print ("The connection is closed")

#Displays the table of the word
def select( word ):

   #create a cursor for the select
   cur = db.cursor();

   #execute an sql query
   cur.execute("SELECT * FROM _"+word);

   #Iterate 
   for row in cur.fetchall() :
      for i in range (0, len(row)) :
         field = str(row[i]);
         print (field);

   # close the cursor
   cur.close();

   print ("Display Sucessfull");

#Checks if a table exists, returns true if it doesnt and
#returns false if it does.
def isNotTable(word):
   cur = db.cursor();
   field=0;
   cur.execute("SELECT COUNT(*)FROM information_schema.tables WHERE table_schema = 'engr103' AND table_name = '_"+word+"'")
   for row in cur.fetchall() :
       #data from rows
       for i in range (0, len(row)) :
        field = str(row[i]);
   cur.close();
   field=int(field)
   if field==0:
      return 1;
   else:
      return 0;
   
#Insert function for a table of mainword with  
def insert( mainword, word, isFirstFollowing=1):

   #create mutiple cursors to prevent overlapping queries
   cur1 = db.cursor();
   cur2 = db.cursor();
   cur3 = db.cursor();
   field=0;

   #Check if table exists, if it doesnt create the specified table.
   if isNotTable(mainword):
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

   if isNotTable(mainword):
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
