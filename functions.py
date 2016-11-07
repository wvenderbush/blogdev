import sqlite3 as sql
import hashlib

#CONNECT DATABASE
STORIES = "data/stories.db"

#Initialize databases. Only works once.
def initializeTables():
	db = sql.connect(STORIES)
	c = db.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS accounts (username TEXT NOT NULL, password TEXT NOT NULL)")
	c.execute("CREATE TABLE IF NOT EXISTS entries (storyid INTEGER, content TEXT NOT NULL, entryID INTEGER PRIMARY KEY autoincrement, contributor TEXT NOT NULL, timestamp TEXT NOT NULL)")
	c.execute("CREATE TABLE IF NOT EXISTS stories (storyid INTEGER PRIMARY KEY, title TEXT NOT NULL)")
	db.commit()
	db.close()

def getstoryID(title):
	db = sql.connect(STORIES)
	c = db.cursor()
	l = c.execute("SELECT storyid FROM stories WHERE title = ?" , (title,))
	id = c.fetchall()
	return id[0][0]



#=============================================================AUTHENTICATION==================================================================
def register(username, password):
	hashpass = hashlib.sha224(password).hexdigest()
	creds = (username,hashpass,)
	db = sql.connect(STORIES)
	c = db.cursor()
	users = c.execute("SELECT username FROM accounts WHERE username = ?", (username,))
	if len(c.fetchall()) == 0 and len(password) >= 3:
		c.execute("INSERT INTO accounts (username,password) VALUES (?,?)", creds)
		db.commit()
		return True
	else:
		return False

def login(username,password):
	hashpass = hashlib.sha224(password).hexdigest()
	db = sql.connect(STORIES)
	c = db.cursor()
	users = c.execute("SELECT password FROM accounts WHERE username = ?", (username,))
	data = users.fetchall()
	if len(data) == 0:
		return False
	elif data[0][0] == hashpass:
		return True
	db.commit()

def changePass(username,oldpass,newpass):
        hashnewpass = hashlib.sha224(newpass).hexdigest()
        db = sql.connect(STORIES)
        c = db.cursor()
	exists = login(username,oldpass)
	if exists:
		c.execute("UPDATE accounts SET password = ? WHERE username = ?", (hashnewpass,username,))
		db.commit()
		return True
	else:
		return False
#========================================================GENERIC CREATE FUNCTIONS=============================================================
def newStory(title, content, contributor, timestamp):
	db = sql.connect(STORIES)
	c = db.cursor()
	c.execute("INSERT INTO stories (title) VALUES (?)", (title,))
	c.execute("INSERT INTO entries (storyid, content, contributor, timestamp) VALUES(?, ?, ?, ?)" , (c.lastrowid, content.strip(), contributor, timestamp,))
	db.commit()

def newEntry(storyid, content, contributor, timestamp):
	db = sql.connect(STORIES)
	c = db.cursor()
	c.execute("INSERT INTO entries (storyid, content, contributor, timestamp) VALUES(?, ?, ?, ?)" , (storyid, content, contributor, timestamp,))
	db.commit()

#=============================================================================================================================================


#===========================================================OUTPUT FUNCTIONS=================================================================

def getTitle(storyID):
    db = sql.connext(STORIES)
    c = db.cursor()
    data = c.execute("SELECT * FROM stories WHERE stories.storyid == ?", (storyid,))
    return data.fetchone()[1]


#how many entries in a story
def returnNumEntries(storyid):
	db = sql.connect(STORIES)
	c = db.cursor()
	count = 0
	data = c.execute("SELECT * FROM entries WHERE entries.storyid = ?" , (storyid,))
	for row in data:
		count+=1
	return count


#Returns a list of all posts a user has contributed to
def returnContributed(username):
	db = sql.connect(STORIES)
	c = db.cursor()
	data = c.execute("SELECT DISTINCT storyid FROM entries WHERE entries.contributor == ? ORDER BY timestamp ASC" , (username,))
	stories = []
	for item in data:
		stories.append(item[0])	#Item[0] = storyid
	return stories

#Returns one entire story as a list
def returnStory(storyid):
	db = sql.connect(STORIES)
	c = db.cursor()
	data = c.execute("SELECT * FROM entries WHERE entries.storyid == ? ORDER BY entryID ASC" , (storyid,))
	story = []
	for item in data:
		story.append(item[1]) # Item 1 = Story content of one entry
	return story

#Returns a list of all contributors to a story in order
def returnContributors(storyid):
	db = sql.connect(STORIES)
	c = db.cursor()
	data = c.execute("SELECT * FROM entries WHERE entries.storyid == ? ORDER BY entryID ASC" , (storyid,))
	contributors = []
	for item in data:
		contributors.append(item[3]) #Item[3] = contributor
	return contributors

def returnLatest(numStories):
	db = sql.connect(STORIES)
	c = db.cursor()
	data = c.execute("SELECT DISTINCT storyid FROM entries ORDER BY entries.entryID DESC LIMIT ?" , (numStories,))
	stories = []
	for item in data:
		stories.append(item[0])
	return stories

#Returns list of all completed story ids ordered
def returnFinished(sortOrder):
	db = sql.connect(STORIES)
	c1 = db.cursor()
	c2 = db.cursor()
	stories = c1.execute("SELECT DISTINCT storyid FROM entries ORDER BY ? ASC" , (sortOrder,))
	storyList = []
	for story in stories:
		l = list(c2.execute("SELECT * FROM entries WHERE entries.storyid == ?" , story))
		if len(l) >= 10:
			storyList.append(story[0])
	return storyList

def returnLastEntry(storyid):
	db = sql.connect(STORIES)
	c = db.cursor()
	data = c.execute("SELECT * FROM entries WHERE entries.storyid == ? ORDER BY timestamp DESC", (storyid,))
	entry = data.fetchone()
	return entry

def returnStoryInfo(storyid):
	content = []
	contributors = []
	timestamp = []
	db = sql.connect(STORIES)
	c = db.cursor()
	data = c.execute("SELECT content,contributor,timestamp FROM entries WHERE storyid = ?" , (storyid,))
	for row in data:
		content.append(row[0])
		contributors.append(row[1])
		timestamp.append(row[2])
	return (content, contributors, timestamp,)
#==============================================================================================================================================


#=============================================================FOR DISPLAY FUNCTIONS============================================================

#Returns a tuple (All titles of stories user contributed to,
#                 all stories contents of the contributed to stories,
#                 all contributors of the respective stories)
#
# Tuple represented in components : ([], [][], [][])
# For my account/my stories page
def myStoryList(username):
	db = sql.connect(STORIES)
	c = db.cursor()
	myStories = returnContributed(username)
	allStories = []
	allContributors = []
	allTitles = []

	for storyid in myStories:
		allStories.append(returnStory(storyid))
		allContributors.append(returnContributors(storyid))

		data = c.execute("SELECT * FROM stories WHERE stories.storyid == ?" , (storyid,))
		entry = data.fetchone()
		if entry:
			allTitles.append(entry[1]) #First (and only) entry fetch. fetch[1] = title

	return (allTitles, allStories, allContributors)

def myStoryListID(username):
	db = sql.connect(STORIES)
	c = db.cursor()
	allIDs = []
	allTitles = []
	myStories = returnContributed(username)

	for storyid in myStories:
		allIDs.append(storyid);
		data = c.execute("SELECT * FROM stories WHERE stories.storyid == ?" , (storyid,))
		allTitles.append(data.fetchone()[1]) #First (and only) entry fetch. fetch[1] = title

	return (allIDs, allTitles,)

def myStoryListDict(username):
	db = sql.connect(STORIES)
	c = db.cursor()
	storyDict = {}
	myStories = returnContributed(username)
	for storyid in myStories:
		data = c.execute("SELECT * FROM stories WHERE stories.storyid == ?" , (storyid,))
		title = data.fetchone()
		if title:
			title = title[1] #First (and only) entry fetch. fetch[1] = title
		storyDict[storyid] = title
	return storyDict


#Returns the list of stories for the main page
def menuStories(numStories):
	db = sql.connect(STORIES)
	c = db.cursor()
	latestStories = returnLatest(numStories)
	latestEntries = []
	latestTitles = []
	latestTimes = []
	for story in latestStories:
		if returnNumEntries(story) < 10:
			data = c.execute("SELECT * FROM entries WHERE entries.storyid == ? ORDER BY entryID DESC" , (story,))
			entry = data.fetchone()
			if entry:
				latestEntries.append(entry[1]) #Entry[1] = content
				latestTimes.append(entry[4])
			data = c.execute("SELECT * FROM stories WHERE stories.storyid == ?" , (story,))
			entry = data.fetchone()
			if entry:
				latestTitles.append(entry[1]) #Entry[1] = title
	return (latestTitles, latestStories, latestEntries,latestTimes,)


#Returns the list for all stories that were finished. To be used for the library
def libraryStories():
	db = sql.connect(STORIES)
	c = db.cursor()
	allStories = returnFinished('storyid')
	allEntries = []
	allTitles = []
	for story in allStories:
		data = c.execute("SELECT * FROM entries WHERE entries.storyid == ? ORDER BY entryID ASC" , (story,))
		entries = data.fetchall()
		for entry in entries:
			allEntries.append(entry[1])
		data = c.execute("SELECT title FROM stories WHERE storyid == ?", (story,))
		entry = data.fetchone()
		if entry:
			allTitles.append(entry[0])
	return (allTitles, allStories, allEntries,)

def libraryStoriesDict():
	db = sql.connect(STORIES)
	c = db.cursor()
	tup = tuple(returnFinished('storyid'))
	if len(tup) == 1:
		strtup = str(tup).replace(",","")
	else:
		strtup = str(tup)
	timeStories = "SELECT * FROM stories WHERE storyid in " + strtup + "ORDER BY storyid ASC"
	list = c.execute(timeStories)
       	storyDict = []
	for i in list:
		storyDict.append(i)
	return storyDict

def libraryStoriesDictAlpha():
	db = sql.connect(STORIES)
	c = db.cursor()
	dict = []
	tup = tuple(returnFinished('storyid'))
	if len(tup) == 1:
		strtup = str(tup).replace(",","")
	else:
		strtup = str(tup)
	top = "SELECT * FROM stories WHERE storyid in " + strtup + "ORDER BY title COLLATE NOCASE"
	alphaOrder = c.execute(top)
	for i in alphaOrder:
		dict.append(i)
	return dict

def storyExists(title):
	db = sql.connect(STORIES)
	c = db.cursor()
	comp = ""
	comp = c.execute("SELECT title FROM  stories WHERE title = ?", (title,))
	if comp == "":
		return False
	else:
		return True

#=============================================================================================================================================
