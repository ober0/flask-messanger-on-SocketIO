document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

    // Присоединение к комнате чата при загрузке страницы
    let senderID = document.getElementById('sender-id').value;
    let groupID = document.getElementById('group-id').value;
    let roomName = 'group&' + groupID
    socket.emit('joinGroup', { room: roomName });

    document.getElementById('send_msg').addEventListener('click', function () {
        const messageInput = document.getElementById('message');
        const groupID = document.getElementById('group-id').value;
        const message = messageInput.value.trim();
        if (message !== '') {
            socket.emit('send_group_message', { message: message, groupId:groupID, room: roomName });
            messageInput.value = '';
        }
    })


    // Обработка получения сообщения от сервера
    socket.on('groupe_message', (data) => {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        if (data.sender_id == document.getElementById('sender-id').value){
            messageElement.classList.add('self')
        }
        messageElement.innerText = `${data.sender_name}: ${data.message}`;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
});
