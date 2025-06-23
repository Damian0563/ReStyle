from flask import Blueprint,render_template,url_for,request,flash,redirect, Response, send_file
#from flask_socketio import send,emit,join_room,send,SocketIO
from pymongo import MongoClient
from bson import ObjectId
import random
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
load_dotenv()


service=Blueprint('service',__name__)
@service.route('/home/<id>/<page>',methods=['GET','POST'])
def main(id,page):
    if request.method=="GET":
        username=get_user_by_id(id)[0]
        email=get_user_by_id(id)[1]
        picture=get_user_by_id(id)[2]
        client = MongoClient('localhost', 27017)
        db = client.restyle
        chats=db.chats
        products=db.products
        all_chats=[]
        listings=[]
        i=0
        j=0
        first=chats.find({"user1":id})
        second=chats.find({"user2":id})
        for entry in first:
            all_chats.append((entry['user2'],get_user_by_id(entry['user2'])[0],entry['messages']))
        for entry in second:
            all_chats.append((entry['user1'],get_user_by_id(entry['user1'])[0],entry['messages']))
        try:
            page=int(page)
            if page<=0:
                page=0
                i=0
                j=0
                for entry in products.find():
                    if str(entry['user'])!=str(id):
                        if j>=8*page:
                            listings.append(entry)
                            i+=1
                            if i>page+7:
                                break
                        j+=1
                return render_template('service.html',id=id,page=0,all_chats=all_chats,listings=listings)
            raise ValueError
        except ValueError:
            page=0
            i=0
            j=0
            for entry in products.find():
                print(entry)
                if str(entry['user'])!=str(id):
                    if j>=8*page:
                        listings.append(entry)
                        i+=1
                        if i>page+7:
                            break
                    j+=1
            return render_template('service.html',id=id,page=0,all_chats=all_chats,listings=listings)
    if request.method=="POST":
        product_name=request.form.get("title")
        price=request.form.get("price")
        description=request.form.get("description")
        try:
            price = int(price)
        except ValueError:
            flash('Price must be an integer')
            return render_template('service.html', picture=picture, id=id, all_chats=all_chats,listings=listings,page=page)
        if len(description) == 0 or len(product_name) == 0:
            flash('Invalid data in input fields')
            return render_template('service.html',picture=picture,id=id,all_chats=all_chats,listings=listings,page=page)
        if 'photo' in request.files and request.files['photo'].filename!="":
            ph=request.files['photo']
            # mongo.save_file(profile_image.filename,profile_image)
            filename=secure_filename(ph.filename)
            mimetype=ph.mimetype
            Img=ph.read()
            products.insert_one({"user":ObjectId(id),"username":username,"filename":filename,"mimetype":mimetype,"img":Img,"product_name":product_name,"price":price,"description":description,"gen_id":random.randint(1,1000000)})
            return render_template('service.html',picture=picture,id=id,all_chats=all_chats,listings=listings,page=page)
        else:
            flash('Upload a picture of the product')
            return render_template('service.html',picture=picture,id=id,all_chats=all_chats,listings=listings,page=page)
    return render_template('service.html',picture=picture,id=id,all_chats=all_chats,listings=listings,page=page)

@service.route('/messages/<id>/<connect>/<room>',methods=['GET','POST'])
def messages(id,connect,room):
    picture=get_user_by_id(id)[2]
    img=get_user_by_id(id)[4]
    username=get_user_by_id(id)[0]
    client = MongoClient('localhost', 27017)
    db = client.restyle
    chats=db.chats
    all_chats=[]
    first=chats.find({"user1":id})
    second=chats.find({"user2":id})
    for entry in first:
        all_chats.append((entry['user2'],get_user_by_id(entry['user2'])[0],entry['messages']))
    for entry in second:
        all_chats.append((entry['user1'],get_user_by_id(entry['user1'])[0],entry['messages']))
    current=[]
    connect1=connect
    connect=get_id_by_name(connect)
    first=chats.find({"user1":id,"user2":connect})
    second=chats.find({"user1":connect,"user2":id})
    for entry in first:
        for input in entry['messages']:
            current.append(input)
    for entry in second:
        for input in entry['messages']:
            current.append(input)
    if request.method=="POST":
        new=request.form.get("convo")
        current.append([id,new])
        chats.update_one({"user1":connect,"user2":id},{"$set":{'messages':current}})
        chats.update_one({"user1":id,"user2":connect},{"$set":{'messages':current}})
        #return render_template('direct_messages.html',username=username,id=id,connect=connect,img=img,picture=picture,all_chats=all_chats,current=current,connect1=connect1)
        del current[-1]
    return render_template('direct_messages.html',username=username,id=id,connect=connect,img=img,picture=picture,all_chats=all_chats,current=current,connect1=connect1,room=room)

@service.route('/profile/<id>/<bool>/<inc>/<page>',methods=['GET','POST'])
def profile(id,bool,inc,page):
    username=get_user_by_id(id)[0]
    email=get_user_by_id(id)[1]
    picture=get_user_by_id(id)[2]
    about=get_user_by_id(id)[3]
    img=get_user_by_id(id)[4]
    client=MongoClient('localhost',27017)
    db=client.restyle
    listings=db.products
    entries=listings.find({"user":ObjectId(id)})
    my_listings=[]
    i=0
    j=0
    try:
        page=int(page)
        if page<0:
            flash('Invalid request')
            return render_template('profile.html',id=id,picture=picture,username=username,email=email,about=about,img=img,my_listings=my_listings,inc=inc,page=0,bool=bool)
    except ValueError:
        flash('Invalid request')
        return render_template('profile.html',id=id,picture=picture,username=username,email=email,about=about,img=img,my_listings=my_listings,inc=inc,page=0,bool=bool)
    for entry in entries:
        if j>8*page or j==0:
            my_listings.append(entry)
            i+=1
            if i>page+7:
                break
        j+=1
    if request.method=='POST':
        if(bool=='true'):
            NewUsername=request.form.get('username')
            NewEmail=request.form.get('email')
            NewAbout=request.form.get('about')
            users=db.users
            if NewEmail is None:
                NewEmail=email
            if NewUsername is None:
                NewUsername=username
            if NewAbout is None:
                NewAbout=about

            if 'profile_image' in request.files and request.files['profile_image'].filename!="":
                profile_image=request.files['profile_image']
                # mongo.save_file(profile_image.filename,profile_image)
                filename=secure_filename(profile_image.filename)
                mimetype=profile_image.mimetype
                Img=profile_image.read()
                users.update_one({"_id":ObjectId(id)},{"$set":{"picture":filename,"mimetype":mimetype,"img":Img}})
            users.update_one({"_id":ObjectId(id)},{"$set":{"username":NewUsername,"email":NewEmail,"about":NewAbout}})
            username=get_user_by_id(id)[0]
            email=get_user_by_id(id)[1]
            picture=get_user_by_id(id)[2]
            about=get_user_by_id(id)[3]
            img=get_user_by_id(id)[4]
            return render_template('profile.html',id=id,picture=picture,username=username,email=email,about=about,img=img,my_listings=my_listings,inc=inc,page=page,bool=bool)
        else:
            flash('Invalid permissions')
            return render_template('profile.html',id=id,picture=picture,username=username,email=email,about=about,img=img,my_listings=my_listings,inc=inc,page=page,bool=bool)
    return render_template('profile.html',id=id,picture=picture,username=username,email=email,about=about,img=img,my_listings=my_listings,inc=inc,page=page,bool=bool)

@service.route('/delete/<del_id>/<id>/<bool>/<inc>/<page>',methods=['GET'])
def delete_product(del_id,id,bool,inc,page):
    client=MongoClient('localhost',27017)
    db=client.restyle
    listings=db.products
    listings.delete_one({"gen_id":int(del_id)})    
    return redirect(url_for('service.profile',id=id,bool=bool,inc=inc,page=page))
    
def get_user_by_id(id):
    id=ObjectId(id)
    client=MongoClient('localhost',27017)
    db=client.restyle
    users=db.users
    for user in users.find({"_id":id}):
        return (user['username'],user['email'],user['picture'],user['about'],user['img'])
    return False

def get_id_by_name(name):
    client=MongoClient('localhost',27017)
    db=client.restyle
    users=db.users
    for user in users.find({"username":name}):
        if user:
            return str(user['_id'])
        return False
    return False

@service.route('/get_image/<id>')
def get_image(id):
    client = MongoClient('localhost', 27017)
    db = client.restyle
    users = db.users
    user = users.find_one({"_id": ObjectId(id)})
    if user and 'img' in user and 'mimetype' in user:
        return Response(user['img'], mimetype=user['mimetype'])
    else:
        image_path = r'C:\Users\damia\Desktop\ReStyle\static\images\default.webp'
        return send_file(image_path,mimetype='image/jpeg')

@service.route('/get_image_prod/<id>')
def get_image_prod(id):
    client = MongoClient('localhost', 27017)
    db = client.restyle
    products=db.products
    pic = products.find_one({"gen_id": int(id)})
    if pic and 'img' in pic and 'mimetype' in pic:
        return Response(pic['img'], mimetype=pic['mimetype'])
    else:
        image_path = r'C:\Users\damia\Desktop\ReStyle\static\images\default.jpg'
        return send_file(image_path,mimetype='image/jpeg')

@service.route('/messages/<id>',methods=['GET','POST'])
def message_hub(id):
    username=get_user_by_id(id)[0]
    email=get_user_by_id(id)[1]
    picture=get_user_by_id(id)[2]
    about=get_user_by_id(id)[3]
    img=get_user_by_id(id)[4]

    client = MongoClient('localhost', 27017)
    db = client.restyle
    chats=db.chats

    all_chats=[]
    first=chats.find({"user1":id})
    second=chats.find({"user2":id})
    for entry in first:
        all_chats.append((entry['user2'],get_user_by_id(entry['user2'])[0],entry['room'],entry['messages']))
    for entry in second:
        all_chats.append((entry['user1'],get_user_by_id(entry['user1'])[0],entry['room'],entry['messages']))
    if request.method=='POST':
        link=request.form.get("link")
        if get_id_by_name(link):
            count=0
            for user in chats.find({"user1":id,"user2":get_id_by_name(link)}):
                if user:
                    count+=1
            for user in chats.find({"user1":get_id_by_name(link),"user2":id}):
                if user:
                    count+=1
            if count>0:
                flash(f"Conversation with {link} already exsists")
                return render_template('messagesHUB.html',id=id,picture=picture,img=img,username=username,all_chats=all_chats)
            else:
                room=str(uuid4())
                chats.insert_one({"room":room,"user1":id,"user2":get_id_by_name(link),"messages":{}})
                all_chats=[]
                first=chats.find({"user1":id})
                second=chats.find({"user2":id})
                for entry in first:
                    all_chats.append((entry['user2'],get_user_by_id(entry['user2'])[0],entry['room'],entry['messages']))
                for entry in second:
                    all_chats.append((entry['user1'],get_user_by_id(entry['user1'])[0],entry['room'],entry['messages']))
                return render_template('messagesHUB.html',id=id,picture=picture,img=img,username=username,all_chats=all_chats)
        else:
            flash("Such a user does not exsist")
            return render_template('messagesHUB.html',id=id,picture=picture,img=img,username=username,all_chats=all_chats)
    return render_template('messagesHUB.html',id=id,picture=picture,img=img,username=username,all_chats=all_chats)


