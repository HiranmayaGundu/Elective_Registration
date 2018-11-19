# Please follow the following naming convention: long_function_name(var_one,var_two)
from flask import Flask, flash,session, render_template, request, redirect, Response ,jsonify, json, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from string import Template
import pymysql
import smtplib
import datetime


app = Flask(__name__)
app.secret_key = 'totally a secret lolz'
# db = pymysql.connect("localhost", "root", "root", "SE_Project")
db = pymysql.connect("localhost", "root", "", "SE_Project", charset="latin1")
cursor = db.cursor()


@app.route('/')
def index():
    '''This function renders the index page of the assignment site'''
    return render_template('landing.html')

@app.route('/signin')
def signin():
    '''This function renders the sign in page.'''
    return render_template('signin.html')


if __name__ == '__main__':
# run!
    app.run(debug=True)