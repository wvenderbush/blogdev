import random, functions, hashlib, sqlite3, time
from flask import Flask, render_template, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = '\xe9$=P\nr\xbc\xcd\xa5\xe5I\xba\x86\xeb\x81L+%,\xcb\xcb\xf46d\xf9\x99\x1704\xcd(\xfc'

f = 'data/stories.db'
db = sqlite3.connect(f)
c = db.cursor()

@app.route("/", methods = ['POST','GET'])
def new():
	return render_template('home.html', title = "ComboChronicles", titles_stories = zip(functions.menuStories(10)[0], functions.menuStories(10)[1], functions.menuStories(10)[2], functions.menuStories(10)[3]))

@app.route("/<message>", methods = ['POST','GET'])
def home(message):
	return render_template('home.html', title = "ComboChronicles", message = message, titles_stories = zip(functions.menuStories(10)[0], functions.menuStories(10)[1], functions.menuStories(10)[2], functions.menuStories(10)[3]))

@app.route("/login/", methods = ['POST','GET'])
def login():
	return render_template('login.html', title = "login")

@app.route("/authenticate/", methods = ['POST','GET'])
def authenticate():
	if request.method == 'POST':
		username = request.form['user']
		password = request.form['pass']
		hashpass = hashlib.sha224(password).hexdigest()
		if 'login' in request.form:
			if functions.login(username,password):
				session['username'] = username
				return redirect(url_for("home",message = "Login Successful"))
			else:
				return redirect(url_for("home",message = "Login Failed"))
		else:
			if functions.register(username,password):
				return redirect(url_for("home",message = "Registration Successful"))
			else:
				return redirect(url_for("home",message = "Registration Failed"))
	else:
		return redirect(url_for("login"))

@app.route("/logout/")
def logout():
	session.pop('username')
	return redirect(url_for("home", message = "Successfully logged out"))

@app.route("/newentry/<int:storyid>/<storytitle>/", methods=['GET','POST'])
def newentry(storyid, storytitle):
	if storyid in functions.returnContributed(session['username']):
	 	return redirect(url_for("story", storyid = storyid, storytitle = storytitle))
	if request.method == 'POST':
			storyTitle = storytitle
			storyID = storyid
			entry = request.form['entry']
			functions.newEntry(storyID,entry,session['username'],time.strftime("%Y-%m-%d %H:%M:%S"))
			return redirect(url_for("home", message = "Awesome, new entry for " + storyTitle + " submitted!"))
	else:
		statlist = functions.returnLastEntry(storyid)
		contentholder = functions.returnStory(storyid)
		return render_template('newentry.html', numentries = functions.returnNumEntries(storyid), title = "New Entry", id = storyid, story = storytitle, content = functions.returnStory(storyid)[-1], stats = 'by ' + statlist[3] + " at " + statlist[4])


@app.route("/newstory/", methods=['GET','POST'])
def newstory():
	if request.method == 'POST':
		title = request.form['title']
		story = request.form['story']
		functions.newStory(title,story,session['username'],time.strftime("%Y-%m-%d %H:%M:%S"))
		return redirect(url_for('home', message = "Awesome, you started a new story!"))
	else:
		return render_template('newstory.html', title = "Create Story")

@app.route("/account/", methods=['GET','POST'])
def account():
	if request.method == 'POST':
		oldpass = request.form['oldpass']
		newpass = request.form['newpass']
		if functions.changePass(session['username'],oldpass,newpass):
			return render_template('account.html', title = "My Account", userstories = functions.myStoryListDict(session['username']), message = "Successfully changed password")
		else:
			return render_template('account.html', title = "My Account", userstories = functions.myStoryListDict(session['username']), message = "Password change failed")
	else:
		return render_template('account.html', title = "My Account", userstories = functions.myStoryListDict(session['username']))


@app.route('/user/<username>/')
def show_user_profile(username):
	return render_template('account.html', title =  username+ "'s Account", user = username, userstories = functions.myStoryListDict(username))


@app.route("/library/", methods=['GET','POST'])
def library():
	return render_template('library.html', title = "Library", stories = functions.libraryStoriesDict())

@app.route("/library/<sort>", methods=['GET','POST'])
def libsort(sort):
	if sort == "alpha":
		return render_template('library.html', title = "Library", stories = functions.libraryStoriesDictAlpha(), mode = 0)
 	else:
		return render_template('library.html', title = "Library", stories = functions.libraryStoriesDict())

@app.route("/about/", methods=['GET','POST'])
def about():
	return render_template('about.html', title = "About")

@app.route("/story/<int:storyid>/<storytitle>/", methods=['GET','POST'])
def story(storyid, storytitle):
	contentlist = functions.returnStoryInfo(storyid)
	howmany = functions.returnNumEntries(storyid)
	contents = contentlist[0]
	users = contentlist[1]
	times = contentlist[2]
	return render_template("story.html", id = storyid, story = storytitle, list = zip(contents, users, times))

if __name__ == "__main__":
	app.debug = True
	functions.initializeTables()
	app.run()
