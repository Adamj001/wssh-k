from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import paramiko
import threading
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# SSH 客户端存储
clients = {}

def ssh_task(sid, hostname, username, password, port=22):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)
        clients[sid] = ssh
        
        channel = ssh.invoke_shell(term='xterm', width=80, height=24)
        clients[sid + '_channel'] = channel
        
        while True:
            data = channel.recv(1024).decode('utf-8')
            if data:
                socketio.emit('output', {'data': data}, room=sid)
                
    except Exception as e:
        socketio.emit('output', {'data': f'Error: {str(e)}'}, room=sid)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('output', {'data': 'Connected to WebSSH server'})

@socketio.on('login')
def handle_login(data):
    hostname = data['hostname']
    username = data['username']
    password = data['password']
    port = data.get('port', 22)
    
    thread = threading.Thread(
        target=ssh_task,
        args=(request.sid, hostname, username, password, port)
    )
    thread.daemon = True
    thread.start()

@socketio.on('input')
def handle_input(data):
    if request.sid in clients:
        channel = clients.get(request.sid + '_channel')
        if channel:
            channel.send(data['data'])

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in clients:
        clients[request.sid].close()
        del clients[request.sid]
        if request.sid + '_channel' in clients:
            del clients[request.sid + '_channel']

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)