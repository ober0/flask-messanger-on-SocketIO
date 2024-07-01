document.addEventListener("DOMContentLoaded", main)
window.addEventListener("pageshow", main);



function main(){
    const socket = io()

    console.log(socket)

    socket.emit('room_for_notify', {})

    socket.on('notify', (data) => {
        let message = data.message
        let from = data.sender_name
        let path = data.path
        console.log(path)
        if (window.location.pathname != path){
            let text = 'Новое сообщение от ' + from + '\n' + 'message'

            let notif = document.getElementById('notification-container')
            notif.classList.remove('hide')
            document.getElementById('path1').value = path
            document.getElementById('type1').innerText = 'Новое сообщение'
            document.getElementById('from1').innerText = 'От:' + from
            document.getElementById('message1').innerText = message
            setTimeout( function () {
                document.getElementById('notification-container').classList.add('hide')
            }, 5000)
        }


    })
}