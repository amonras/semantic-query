var socket = new WebSocket("ws://localhost:8000/ws");

document.getElementById('sendButton').onclick = function() {
    var message = document.getElementById('messageInput').value;
    socket.send(message);
};

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

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
        case 'DisplayDocuments':
            var documentsContainer = document.getElementById('documents');
            var documents = messageData.payload.documents;
            var documentsList = '<ul>';
            for (var i = 0; i < documents.length; i++) {
                documentsList += documents[i];
            }
            documentsList += '</ul>';
            documentsContainer.innerHTML += '<p>Documents available for search:</p>' + documentsList;
            documentsContainer.scrollTop = logs.scrollHeight;
            break;

        // Add more cases here for other message types
        default:
            logs.innerHTML += '<p>Received unknown message type: ' + messageData.type + '</p>';
            logs.scrollTop = logs.scrollHeight;
    }

    var croppedMessage = escapeHtml(event.data).substring(0, 100); // Crop to 100 characters
    messages.innerHTML += '<p>' + croppedMessage + '</p>';
    messages.scrollTop = messages.scrollHeight;
};
