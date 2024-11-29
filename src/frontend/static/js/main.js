var socket = new WebSocket("ws://localhost:8000/ws");

document.getElementById('sendButton').onclick = function() {
    var message = document.getElementById('messageInput').value;
    var messageDTO = {
        type: 'ChatQueryMessage',
        payload: {
            message: message
        }
    };
    socket.send(JSON.stringify(messageDTO));
};

document.getElementById('messageInput').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        document.getElementById('sendButton').click();
    }
});

const divider = document.getElementById('divider');
const left = document.getElementById('documents');
const right = document.getElementById('qa-scroll');

divider.addEventListener('mousedown', (e) => {
    e.preventDefault();
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
});

function onMouseMove(e) {
    const containerOffsetLeft = document.querySelector('.container').offsetLeft;
    const pointerRelativeXpos = e.clientX - containerOffsetLeft;
    const containerWidth = document.querySelector('.container').offsetWidth;
    const leftWidth = (pointerRelativeXpos / containerWidth) * 100;
    const rightWidth = 100 - leftWidth;

    if (rightWidth >= (260 / containerWidth) * 100) { // Ensure right panel's minimum width
        left.style.flexBasis = `${leftWidth}%`;
        right.style.flexBasis = `${rightWidth}%`;
    }
}

function onMouseUp() {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
}

function openDetailsAndParents(detailsElement) {
    let current = detailsElement;

    while (current && current.tagName === 'DETAILS') {
        current.open = true;
        current = current.parentElement.closest('details'); // Find the nearest ancestor <details>
    }
}

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
            // document.querySelector('#my-dropzone').dropzone.options.headers = {'Connection-ID': connectionId};

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
        case 'UnfoldNodes':
            var node_uuids = messageData.payload.node_uuids;
            var nodesList = '<ul>';
            for (var i = 0; i < node_uuids.length; i++) {
                node = document.getElementById(node_uuids[i]);
                nodesList += '<li>' + node + '</li>';
                openDetailsAndParents(node);
            }
            nodesList += '</ul>';
            logs.innerHTML += '<p>Nodes unfolded:</p>' + nodesList;
            logs.scrollTop = logs.scrollHeight;
            break;

        // Add more cases here for other message types
        default:
            logs.innerHTML += '<p>Received unknown message: ' + messageData + '</p>';
            logs.scrollTop = logs.scrollHeight;
    }

    var croppedMessage = escapeHtml(event.data).substring(0, 100); // Crop to 100 characters
    messages.innerHTML += '<p>' + croppedMessage + '</p>';
    messages.scrollTop = messages.scrollHeight;
};
