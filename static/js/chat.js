document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

    // Присоединение к комнате чата при загрузке страницы
    let senderID = document.getElementById('sender-id').value;
    let receiverID = document.getElementById('receiver-id').value;
    let roomName = Math.min(senderID, receiverID) + '&' + Math.max(senderID, receiverID);
    socket.emit('join', { room: roomName });

    document.getElementById('send_msg').addEventListener('click', function () {
        const messageInput = document.getElementById('message');
        const receiverId = document.getElementById('receiver-id').value;
        const message = messageInput.value.trim()
        if (message !== '') {
            console.log(message)
            socket.emit('send_message', { message: message, receiver_id: receiverId, room: roomName });
            messageInput.value = '';
        }
    })


    // Обработка получения сообщения от сервера
    socket.on('message', (data) => {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        if (data.sender_id   == document.getElementById('sender-id').value){
            messageElement.classList.add('self')
        }
        messageElement.innerText = `${data.sender_name}: ${data.message}`;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

    });
});
