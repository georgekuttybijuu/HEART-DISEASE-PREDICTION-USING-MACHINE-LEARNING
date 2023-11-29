from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd
import pickle

app = Flask(__name__)
pipe = pickle.load(open("trained_model.pkl","rb"))
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Initialize the MySQL extension
mysql = MySQL(app)

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cur.fetchone()
        cur.close()  # Close the cursor after fetching data
        if user:
            return render_template('index.html')
        else:
            message = 'Please enter correct email/password!'
    return render_template('login.html', message=message)


@app.route('/predict', methods=['POST'])
def predict():
    age = request.form.get('age')
    gen = request.form.get('gender')
    cp = request.form.get('cp')
    rbps = request.form.get('rbps')
    chol = request.form.get('chol')
    fbp = request.form.get('fbp')
    recg = request.form.get('recg')
    thalach = request.form.get('thalach')
    eia = request.form.get('eia')
    oldpeak = request.form.get('oldpeak')
    spsts = request.form.get('spsts')
    mvcf = request.form.get('mvcf')
    mhra = request.form.get('mhra')


    #print(age,gen,cp,rbps,chol,fbp,recg,thalach,eia,oldpeak,spsts,mvcf,mhra)
    input = pd.DataFrame([[age,gen,cp,rbps,chol,fbp,recg,thalach,eia,oldpeak,spsts,mvcf,mhra]],columns=['age', 'gender', 'cp', 'rbps', 'chol', 'fbp', 'recg', 'thalach', 'eia', 'oldpeak', 'spsts', 'mvcf', 'mhra'])
    prediction = pipe.predict(input)[0]
    if(prediction==1):
        return render_template("index.html", prediction_text = "Disease is affected...immediately consult a doctor!!!")
    else:
        return render_template("index.html", prediction_text = "Disease is not affected")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cur.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not name or not password or not email:
            message = 'Please fill out the form!'
        else:
            cur.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (name, email, password,))
            # cur.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (name, email, password,))
            mysql.connection.commit()
            message = 'You have successfully registered!'
            cur.close()  # Close the cursor after committing changes
    return render_template('register.html', message=message)


if __name__ == "__main__":
    app.debug = True
    app.run()
