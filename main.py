from flask import Blueprint,render_template,url_for,request,flash,redirect
from werkzeug.security import generate_password_hash,check_password_hash
from pymongo import MongoClient
import re


home=Blueprint('home',__name__)
@home.route('/',methods=['GET','POST'])
def hello():
    return render_template('homepage.html')

@home.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        client=MongoClient('localhost',27017)
        db=client.restyle
        users=db.users
        email=request.form.get('email')
        password=request.form.get('password')
        username=request.form.get('username')
        if not validate(email):
            flash('Invalid email')
            return render_template('signup.html')
        else:
            if len(list(users.find({"email":email})))>0:
                flash('Account already registered under provided email')
                return render_template('signup.html')
            else:
                flash('Signed up successfuly')
                if check_unique_name(username):
                    users.insert_one({"username":username,"email":email,"password":generate_password_hash(password),"picture":"default","about":"none","img":"default"})
                    return render_template('signup.html')
                else:
                    flash('Such an username is taken')
                    return render_template('signup.html')
    return render_template('signup.html')

def validate(email):
    pattern=re.search(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$",email)
    if pattern:
        return True
    return False

def check_unique_name(name):
    client=MongoClient('localhost',27017)
    db=client.restyle
    users=db.users
    for user in users.find({"username":name}):
        if user:
            return False
    return True

@home.route('/signin',methods=['GET','POST'])
def signin():
    if request.method=="POST":
        client=MongoClient('localhost',27017)
        db=client.restyle
        users=db.users
        email=request.form.get('email')
        password=request.form.get('password')
        for user in users.find({"email":email}):
            if check_password_hash(user['password'],password):
                id=user['_id']
                return redirect(url_for('service.main',id=id,page=0))
            else:
                flash('Invalid credentials')
                return render_template('signin.html')
        flash('Invalid credentials')
        return render_template('signin.html')
    return render_template('signin.html')



