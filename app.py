#Importing the Libraries
import numpy as np
from flask import Flask, request,render_template, session, redirect
from flask_cors import CORS
from config import Config
from flaskext.mysql import MySQL
import os
# from sklearn.externals import joblib
import pickle
import nltk
#from nltk.corpus import stopwords
#from nltk.tokenize import word_tokenize, sent_tokenize
# nltk.download('punkt')
import flask
import html
import os
import newspaper
from newspaper import Article
import urllib

#Loading Flask and assigning the model variable
app = Flask(__name__)
CORS(app)
app=flask.Flask(__name__,template_folder='templates')

app.config.from_object(Config)
mysql = MySQL()

mysql.init_app(app)

with open('model.pickle', 'rb') as handle:
	model = pickle.load(handle)

@app.route('/')
def index():
    return render_template('index.html', response='')
    
@app.route('/about')
def about():
    return render_template('about.html', response='')

@app.route('/authentication')
def authentication():
    if 'fake_user' in session :
        return redirect('main')
    return render_template('authentication.html', response='')

@app.route('/privacypolicy')
def privacypolicy():
    return render_template('privacypolicy.html', response='')

@app.route('/termsofservice')
def termsofservice():
    return render_template('termsofservice.html', response='')

@app.route('/main')
def main():
    return render_template('main.html', response='')

@app.route('/prepredict')
def prepredict():
    return render_template('prepredict', response='')

@app.route('/logout')
def logout():
    if 'fake_user' in session:
        session.pop('fake_user')
    return redirect('/')

@app.route('/previouspredictions')
def previouspredictionst():
    data = previouspredictions()
    print(data)
    return render_template('previouspredictions.html', data=data)




#Receiving the input url from the user and using Web Scrapping to extract the news content
@app.route('/predict', methods=['GET','POST'])
def predict():
    if request.method == 'GET':
        return render_template('main.html')
    else:
        url =request.get_data(as_text=True)[5:]
        url = urllib.parse.unquote(url)
        article = Article(str(url))
        article.download()
        article.parse()
        article.nlp()
        news = article.summary
        #Passing the news article to the model and returing whether it is Fake or Real
        pred = model.predict([news])

        result = format(pred[0])
        user_id = session['fake_user'][0]
        summary = html.unescape(news)
        summary = summary.replace("'","")
        insertPredictionQuery(user_id, url,summary, result)
        return render_template('main.html', news=news, prediction_text='The news is "{}"'.format(pred[0]))

@app.route('/login',methods=['POST'])
def login():
    if not request.form['login-username'] or not request.form['login-password']:
        return render_template('authentication.html', response='Username and Password required')

    username = request.form['login-username']
    password = request.form['login-password']

    if checkLogin(username, password):
        session['fake_user'] = getUser(username)
        return redirect('/main')
    else:
        return render_template('authentication.html', responce='Invalid Credentials')


def checkLogin(username, password):
    conn = mysql.connect()
    cursor = conn.cursor()
    test = cursor.execute("SELECT id FROM users WHERE username =  '%s' AND password='%s' " % (username,password))
    return test

def getUser(username):
    conn = mysql.connect()
    cursor = conn.cursor()
    test = cursor.execute("SELECT * FROM users WHERE username =  '" + username + "' ")
    if test:
        return cursor.fetchone()

def insertPredictionQuery(user_id, url,summary, result):
    conn = mysql.connect()
    cursor = conn.cursor()
    test = cursor.execute("INSERT INTO user_predictions(user_id, url, summary, result) VALUES ( '%s', '%s', '%s',  '%s')" % (user_id, url, summary, result))
    conn.commit()
    return test

def previouspredictions():
    user_id = session['fake_user'][0]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_predictions")
    data = cursor.fetchall()
    conn.close()
    return data
    

@app.route('/register', methods=['POST'])
def register():
    if not request.form['username'] or not request.form['password'] or not request.form['fullname']:
        return render_template('index.html', response='Username and Password required')

    fullname = request.form['fullname']
    username = request.form['username']
    password = request.form['password']
    if insertQuery(fullname, username, password):
        session['fake_user'] = getUser(username)
        return render_template('prepredict.html', response='Registration successful')
    else:
        return render_template('authentication.html', response='Invalid Credentials')


def insertQuery(fullname, username, password):
    conn = mysql.connect()
    cursor = conn.cursor()
    test = cursor.execute("INSERT INTO users (fullname, username, password) VALUES ( '%s', '%s',  '%s')" % (fullname, username, password))
    conn.commit()
    if test:
        return test

if __name__=="__main__":
    port=int(os.environ.get('PORT',5000))
    app.run(port=port,debug=True,use_reloader=True)