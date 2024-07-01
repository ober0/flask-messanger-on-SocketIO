from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Message, Group, GroupMessage, GroupMembers, NotifyAccessChat, NotifyAccessGroup


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app)


@app.route('/')
def index():
    if session.get('auth') and session['auth'] == True:
        users = User.query.filter(User.id != session['id']).all()
        groups = Group.query.all()
        return render_template('index.html', users=users, groups=groups)
    else:
        return redirect(url_for('auth'))


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        name = request.form['name']
        user = User.query.filter_by(name=name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
        session['auth'] = True
        session['id'] = user.id
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('auth.html')


@app.route('/chat/<int:id>')
def chat(id):
    receiver = User.query.filter_by(id=id).first()
    sender_id = session.get('id')
    if receiver:
        messages = Message.query.filter(
            ((Message.sender_id == sender_id) & (Message.receiver_id == id)) |
            ((Message.sender_id == id) & (Message.receiver_id == sender_id))
        ).order_by(Message.timestamp.asc()).all()
        return render_template('chat.html', messages=messages, receiver=receiver, sender=User.query.filter_by(id=sender_id).first())
    else:
        return redirect(url_for('/'))

@app.route('/group/<int:groupID>')
def group_fun(groupID):
    sender_id = session.get('id')
    messages = GroupMessage.query.filter_by(group_id=groupID).order_by(GroupMessage.timestamp.asc()).all()
    group = Group.query.filter_by(id=groupID).first()
    if not group:
        group = Group(name=f"{sender_id}'s group")
        db.session.add(group)
        db.session.commit()
    group_members = GroupMembers.query.filter_by(group_id=groupID).all()
    members = [str(i.user_id) for i in group_members]
    if str(session.get('id')) not in members:
        new_group_member = GroupMembers(user_id=int(session.get('id')), group_id=groupID)
        try:
            db.session.add(new_group_member)
            db.session.commit()
        except:
            db.session.rollback()

    return render_template('GroupChat.html', messages=messages, group=group, sender=User.query.filter_by(id=sender_id).first())

@socketio.on('join')
def join(data):
    if session.get('auth') and session['auth'] == True:
        join_room(f'allMsg&{session["auth"]}')
        print('conn')
    room = data['room']
    join_room(room)
    print(f'Joined room: {room}')


@socketio.on('room_for_notify')
def room_for_notify(data):
    if session['auth']:
        room = f'user{session["id"]}'
        join_room(room)
    else:
        index()

@socketio.on('send_message')
def send_message(data):
    message = data['message']
    sender_id = session.get('id')
    sender_name = User.query.filter_by(id=sender_id).first().name
    receiver_id = data['receiver_id']
    room = data['room']
    receiver = User.query.filter_by(id=receiver_id).first()
    # Сохранение сообщения в базе данных
    msg = Message(sender_id=sender_id, sender_name=sender_name, receiver_id=receiver_id, text=message)
    db.session.add(msg)
    db.session.commit()

    emit('message', {'sender_id': sender_id, 'sender_name': sender_name, 'message': message}, room=room)


    notify_access = NotifyAccessChat.query.filter_by(user_id=receiver_id).filter_by(notify_for_id=sender_id).first()
    if notify_access:
        if notify_access.status == 'on':
            emit('notify', {'sender_name': sender_name, 'message': message, 'path': f'/chat/{sender_id}'}, room=f'user{receiver_id}')


@socketio.on('check-notify-access')
def check_notify_access(data):
    type = data['type']
    _from = data['from']
    to = data['to']

    if type == 'chat':
        try:
            status = NotifyAccessChat.query.filter_by(user_id=_from).filter_by(notify_for_id=to).first().status
        except:
            newStatus = NotifyAccessChat(user_id=_from, notify_for_id=to, status='on')
            db.session.add(newStatus)
            db.session.commit()
            status = newStatus.status
    elif type == 'group':
        try:
            status = NotifyAccessGroup.query.filter_by(user_id=_from).filter_by(notify_for_id=to).first().status
        except:
            newStatus = NotifyAccessGroup(user_id=_from, notify_for_id=to, status='on')
            db.session.add(newStatus)
            db.session.commit()
            status = newStatus.status
    else:
        status = 0

    socketio.emit('result-notify-access', {'status': status})


@socketio.on('do-notify-access')
def do_notify_access(data):
    _from = data['from']
    to = data['to']
    type = data['type']
    status_need = data['status_need']

    if type == 'chat':
        statusQuery = NotifyAccessChat.query.filter_by(user_id=_from).filter_by(notify_for_id=to).first()
        if statusQuery:
            statusQuery.status = status_need
            db.session.commit()
            socketio.emit('result-notify-access', {'status': status_need})
    elif type == 'group':
        statusQuery = NotifyAccessGroup.query.filter_by(user_id=_from).filter_by(notify_for_id=to).first()
        if statusQuery:
            statusQuery.status = status_need
            db.session.commit()
            socketio.emit('result-notify-access', {'status': status_need})



@socketio.on('joinGroup')
def join(data):
    room = data['room']
    join_room(room)


@socketio.on('send_group_message')
def send_message(data):
    message = data['message']
    sender_id = session.get('id')
    sender_name = User.query.filter_by(id=sender_id).first().name
    groupId = data['groupId']
    groupName = Group.query.filter_by(id=groupId).first().name
    room = data['room']

    # Сохранение сообщения в базе данных
    msg = GroupMessage(sender_id=sender_id, sender_name=sender_name, group_id=groupId, text=message)
    db.session.add(msg)
    db.session.commit()

    members_group = GroupMembers.query.filter_by(group_id=groupId).all()
    members = [member.user_id for member in members_group]
    for member in members:
        notify_access = NotifyAccessGroup.query.filter_by(user_id=member).filter_by(notify_for_id=groupId).first()
        if notify_access:
            print(1)
            if notify_access.status == 'on':
                emit('notify', {'sender_name': f'{groupName}:  {sender_name}', 'message': message, 'path': f'/group/{groupId}'},
                     room=f'user{member}')
    emit('groupe_message', {'sender_id': sender_id, 'sender_name': sender_name, 'message': message}, room=room)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, allow_unsafe_werkzeug=True)
