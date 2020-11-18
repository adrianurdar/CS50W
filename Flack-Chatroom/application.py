import os

from flask import Flask, render_template, redirect, jsonify, request, url_for, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_session import Session
from collections import deque
from helper import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Keep track of channels
channelsCreated = []

# Keep track of the users
usersLogged = []

# Keep track of messages
channelsMessages = dict()
userChannelsMessages = dict()

@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channelsCreated, users=usersLogged)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Save the username for future usage

    # Forget any user
    session.clear()

    # Save username from form
    username = request.form.get("username")

    # User is inputting his username
    if request.method == "POST":

        # Validate user input
        if len(username) < 1 or username == '':
            return render_template("error.html", message = "username cannot be empty.", code = 433)

        # Check if username is taken
        if username in usersLogged:
            return render_template("error.html", message = "username already exists.", code = 433)

        # Add the user to the users list
        usersLogged.append(username)

        # Set the channel as a key for messages
        # https://stackoverflow.com/questions/1024847/add-new-keys-to-a-dictionary
        userChannelsMessages[username] = deque()

        # Remember username
        session['username'] = username

        # Keep username on browser even if he's closing it
        session.permanent = True

        # Redirect user to index
        return redirect('/')

    else:
        return render_template('login.html')

@app.route("/logout", methods=['GET'])
def logout():
    # Log out the user

    # Remove the user and username
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    # Forget the session
    session.clear()

    # Redirect user to login
    return redirect('/')

@app.route("/create", methods = ['GET', 'POST'])
def create():
    # Create a new channel

    # Get the new channel name from 
    newChannel = request.form.get('channel')

    # User reached route via POST
    if request.method == 'POST':

        # Check if the channel name exists
        if newChannel in channelsCreated:
            return render_template('error.html', message = "channel already exists.", code = 433)

        # Add channel to the list
        channelsCreated.append(newChannel)

        # Set the channel as a key for messages
        # https://stackoverflow.com/questions/1024847/add-new-keys-to-a-dictionary
        channelsMessages[newChannel] = deque()

        # Redirect the user to the new channel
        return redirect('/channels/' + newChannel)

    # User reached route via GET
    else:
        return render_template('create.html', channels=channelsCreated, users=usersLogged)


@app.route('/empty', methods = ['GET', 'POST'])
def empty():
    return render_template('empty.html')


@app.route('/channels/<channel>', methods=['GET', 'POST'])
@login_required
def enter_channel(channel):
    # Channel page, send and receive messages

    # Updates user's current channel
    session['current_channel'] = channel

    # User gets via POST
    if request.method == 'POST':
        # Redirect user to the main page
        return redirect('/')
    
    # User gets via GET
    else:
        try:
            return render_template('channel.html', channels=channelsCreated, messages=channelsMessages[channel], users=usersLogged)
        except KeyError:
            return redirect('/empty')

@app.route('/users/<user>', methods=['GET', 'POST'])
@login_required
def enter_user_channel(user):
    # Channel page, send and receive messages

    # Updates user's current channel
    session['current_channel'] = user

    # User gets via POST
    if request.method == 'POST':
        # Redirect user to the main page
        return redirect('/')
    
    # User gets via GET
    else:
        try:
            return render_template('users.html', channels=channelsCreated, messages=userChannelsMessages[user], users=usersLogged)
        except KeyError:
            return redirect('/empty')            
           

@socketio.on('joined', namespace='/')
def joined():
    # Announce that the user has entered the channel

    # Save current channel
    room = session.get('current_channel')

    join_room(room)

    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' has entered the channel'},
        room=room)

@socketio.on('left', namespace='/')
def left():
    # Announce that the user has left the channel

    # Save current channel
    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('username') + ' has left the channel'},
        room=room)
    
@socketio.on('send message')
def send_msg(msg, timestamp):
    # Display messages with timestamp

    # Keep track of the channel
    room = session.get('current_channel')

    # Keep track of the latest 100 messages
    if len(channelsMessages[room]) > 100:
        
        # If more than 100 messages, remove the extra
        channelsMessages[room].popleft()

    # Track messages, timestamp and user
    channelsMessages[room].append([timestamp, session.get('username'), msg])

    # Announce messages
    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg},
        room=room)

@socketio.on('send user message')
def send_user_msg(msg, timestamp):
    # Display messages with timestamp

    # Keep track of the channel
    room = session.get('current_channel')

    # Keep track of the latest 100 messages
    if len(userChannelsMessages[room]) > 100:
        
        # If more than 100 messages, remove the extra
        userChannelsMessages[room].popleft()

    # Track messages, timestamp and user
    userChannelsMessages[room].append([timestamp, session.get('username'), msg])

    # Announce messages
    emit('announce user message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg},
        room=room)        