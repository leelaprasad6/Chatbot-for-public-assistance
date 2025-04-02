
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['user_database']
users = db['users']
user_data = db['user_data']

@app.route('/')
def home():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users.find_one({'username': request.form['username']})
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        flash('Invalid username/password combination')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        existing_user = users.find_one({'username': request.form['username']})
        if existing_user is None:
            hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({
                'username': request.form['username'],
                'password': hashed
            })
            return redirect(url_for('login'))
        flash('Username already exists')
    return render_template('signup.html')

@app.route('/submit-data', methods=['GET', 'POST'])
def submit_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_data.insert_one({
            'username': session['username'],
            'name': request.form['name'],
            'age': request.form['age'],
            'occupation': request.form['occupation']
        })
        return redirect(url_for('home'))
    return render_template('submit_data.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
