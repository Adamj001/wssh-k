var term = new Terminal();
var socket = io.connect();

term.open(document.getElementById('terminal'));

socket.on('output', function(data) {
    term.write(data.data);
});

term.onData(function(data) {
    socket.emit('input', {data: data});
});

function connect() {
    var hostname = document.getElementById('hostname').value;
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var port = document.getElementById('port').value || 22;

    document.getElementById('login-form').style.display = 'none';
    document.getElementById('terminal').style.display = 'block';
    
    socket.emit('login', {
        hostname: hostname,
        username: username,
        password: password,
        port: port
    });