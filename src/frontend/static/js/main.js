var socket = new WebSocket("ws://localhost:8000/ws");

document.getElementById('sendButton').onclick = function() {
    var message = document.getElementById('messageInput').value;
    socket.send(message);
};

socket.onmessage = function(event) {
    var messageData = JSON.parse(event.data); // Parse the incoming message as JSON
    var messages = document.getElementById('messages');
    var logs = document.getElementById('logs');

    switch(messageData.type) {
        case 'FileUploaded':
            logs.innerHTML += '<p>File "' + messageData.payload.filename + '" has been uploaded.</p>';
            logs.scrollTop = logs.scrollHeight;
            break;
        case 'ConnectionId':
            connectionId = messageData.payload.connection_id;
            logs.innerHTML += '<p>Connection ID: ' + connectionId + '</p>';
            logs.scrollTop = logs.scrollHeight;

            // Set options for Dropzone
            document.querySelector('#my-dropzone').dropzone.options.headers = {'Connection-ID': connectionId};

            break;
        // Add more cases here for other message types
        default:
            logs.innerHTML += '<p>Received unknown message type: ' + messageData.type + '</p>';
            logs.scrollTop = logs.scrollHeight;
    }

    messages.innerHTML += '<p>' + event.data + '</p>';
    messages.scrollTop = messages.scrollHeight;
};
