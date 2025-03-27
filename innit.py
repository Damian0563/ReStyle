from flask import Flask
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from flask_socketio import join_room, send,emit


app=Flask(__name__)
app.config['SECRET_KEY']='secret1111'
from main import home
from operative import service
app.register_blueprint(home,url_prefix='/')
app.register_blueprint(service,url_prefix='/')
socketio=SocketIO(app,cors_allowed_origins='*')

@socketio.on('join-room')
def join(id):
    join_room(id)

@socketio.on('connect')
def handle_connect():
    print("Client connected!")

@socketio.on('send-message')
def message(data):
    room=data['room']
    text=data['text']
    emit("receive-message",{"text":text,"room":room},room=room,broadcast=True)
    print("Message sent!")

if __name__=='__main__':
    socketio.run(app,host='127.0.0.1',port=5000,debug=True)
