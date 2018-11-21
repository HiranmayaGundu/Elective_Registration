# Please follow the following naming convention: long_function_name(var_one,var_two)
from flask import Flask, flash,session, render_template, request, redirect, Response ,jsonify, json, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://root@localhost/WT2")

import pandas as pd
from string import Template
import pymysql
import datetime
import os


app = Flask(__name__)
app.secret_key = 'totally a secret lolz'
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = PROJECT_HOME + "/documents"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['csv'])

db = pymysql.connect("localhost", "root", "", "WT2")
cursor = db.cursor()

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def create_new_folder(local_dir):
	newpath = local_dir
	if not os.path.exists(newpath):
		os.makedirs(newpath)
	return newpath

@app.route('/')
def index():
    '''This function renders the index page of the assignment site'''
    return render_template('landing.html')

@app.route('/signin')
def signin():
    '''This function renders the sign in page.'''
    if request.method == 'POST':
        if('USN' in session):
            return redirect(url_for('student'))
        elif('vendor_id') in session:
            return redirect(url_for('admin'))
    return render_template('signin.html')

@app.route('/checkid',methods = ['POST'])
def check_id():
    '''This function checks if the email is already in the database, i.e., already registered'''

    Id = request.form['id']

    sql = """SELECT * FROM Student WHERE USN=%s"""
    args =([Id])
    cursor = db.cursor()
    cursor.execute(sql,args)
    results = cursor.fetchall()
    cursor.close()

    # Id is valid
    if results:
        return "False"

    sql = """SELECT * FROM Admin WHERE admin_id=%s"""
    args =([Id])

    cursor = db.cursor()
    cursor.execute(sql,args)
    results = cursor.fetchall()
    cursor.close()

    # ID is valid
    if results:
        return "False"

    # # ID is invalid
    return "True"

@app.route('/dosignin',methods=['POST'])
def do_signin():
    '''This function authenticates the sign in by checking password against database.
    It also creates a session, with the Username stored.
    Redirects to /home so that it makes more sense to user'''
    Id = request.form["id"]
    pwd = request.form["pwd"]

    # Check if customer exists
    cursor = db.cursor()
    sql = "SELECT USN,name,pwd,first_log_in from Student where USN = %s"
    args = ([Id])
    cursor.execute(sql,args)
    results = cursor.fetchall()
    cursor.close()

    if results:
        row = results[0]

        if(check_password_hash(row[2],pwd) and row[3]=='0'):
            # do session stuff
            session.clear()
            session['USN'] = row[0]
            session['name'] = row[1]
            return "True"
        elif row[3]=='1':
            return redirect("/firstsignin")
        else:
            # wrong password, tell user
            session.clear()
            return "False"

    # If we reach here, it means that the either the user is a vendor he has not registered with us yet
    cursor = db.cursor()
    sql = "SELECT admin_id,name,pwd from Admin where admin_id = %s"
    args = ([Id])
    cursor.execute(sql,args)
    results = cursor.fetchall()
    cursor.close()

    # Check if customer exists
    if results:
        row = results[0]
        if(check_password_hash(row[2],pwd)):
            # do session stuff
            session.clear()
            session['admin_id'] = row[0]
            session['name'] = row[1]
            return "True"
        else:
            # wrong password, tell user
            session.clear()
            return "False"
    # If we still reach here, it means that the user is not a registered one
    return "False"

@app.route('/logout', methods=['POST','GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/uploadstudent',methods=['POST'])
def upload_student():
    if 'file' not in request.files:
        abort(401)
    file = request.files['file']
    if file.filename == '':
        abort(401)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if(create_student_db(filename)):
            return "Sucess!"
        else:
            abort(402)
    abort(401)

@app.route('/uploadelectives',methods=['POST'])
def upload_electives():
    if 'file' not in request.files:
        abort(401)
    file = request.files['file']
    if file.filename == '':
        abort(401)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if(create_electives_db(filename)):
            return "Sucess!"
        else:
            abort(402)
    abort(401)

def create_student_db(filename):
    filepath = app.config['UPLOAD_FOLDER'] + "/" + filename
    df = pd.read_csv(filepath)
    col_list = df.columns.values.tolist()
    req_col_list = ['USN','name','courses','sem']
    checkFlag = all(elem in col_list for elem in req_col_list)
    if(len(col_list) == 3 and checkFlag):
        df['pwd'] = df['USN'].values
        df['first_log_in'] = '1'
        print(df.head())
        df.to_sql('Student',engine,if_exists='append')
        return True
    return False

def create_electives_db(filename):
    filepath = app.config['UPLOAD_FOLDER'] + "/" + filename
    df = pd.read_csv(filepath)
    col_list = df.columns.values.tolist()
    req_col_list = ['code','name','prerequistes','sem','pool']
    checkFlag = all(elem in col_list for elem in req_col_list)
    if(len(col_list) == 3 and checkFlag):
        print(df.head())
        df.to_sql('Student',engine,if_exists='replace')
        return True
    return False


if __name__ == '__main__':
# run!
    app.run(debug=True)