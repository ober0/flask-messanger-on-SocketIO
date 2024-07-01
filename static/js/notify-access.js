document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('menu-notify-access-button')

    const socket = io()

    console.log(1)
    let from = document.getElementById('access-sender-id').value
    let to = document.getElementById('access-receiver-id').value
    let type = document.getElementById('type').value
    socket.emit('check-notify-access', {from: from, to: to, type: type})


    socket.on('result-notify-access', (data) => {
        let result = data.status
        if (result == 'on'){
            btn.value = 'Выключить уведомления'
        }
        else if (result == 'off') {
            btn.value = 'Включить уведомления'
        }
    })


    document.getElementById('menu-notify-access-button').addEventListener('click', function () {
        let status_need
        if (this.value == 'Выключить уведомления'){
            status_need = 'off'
        }
        else if (this.value == 'Включить уведомления'){
            status_need = 'on'
        }
        else {
            return false
        }

        socket.emit('do-notify-access', {from: from, to: to, type: type, status_need: status_need})

    })

})


