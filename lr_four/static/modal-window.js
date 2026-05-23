class ModalManager {
    constructor() {
        this.messageModal = new bootstrap.Modal(document.getElementById('messageModal'));
        this.confirmCallback = null
    }

    showMessage(msg, type='info') {
        const modalHeader = document.getElementById('modalHeader')
        const modalBody = document.getElementById('modalMessage')

        // Если сообщение содержит переносы строк, преобразуем в HTML список
        if (msg.includes('\n')) {
            const errors = msg.split('\n').filter(e => e.trim() !== '')
            const errorList = errors.map(error => `<div class="text-start">• ${error}</div>`).join('')
            modalBody.innerHTML = errorList
        } else {
            modalBody.textContent = msg
        }

        modalHeader.className = 'modal-header'
        switch(type) {
            case 'success':
                modalHeader.classList.add('bg-success', 'text-white')
                document.getElementById('messageModalLabel').textContent = 'Успех!';
                break
            case 'danger':
            case 'error':
                modalHeader.classList.add('bg-danger', 'text-white')
                document.getElementById('messageModalLabel').textContent = 'Ошибка!';
                break
            case 'warning':
                modalHeader.classList.add('bg-warning', 'text-black')
                document.getElementById('messageModalLabel').textContent = 'Нет доступа!'
                break
            case 'confirm':
                modalHeader.classList.add('bg-danger', 'text-white')
                document.getElementById('messageModalLabel').textContent = 'Подтверждение';

                const footer = document.getElementById('modalFooter')
                footer.innerHTML = ''
                const btnNo = document.createElement('button')
                btnNo.type = 'button'
                btnNo.classList.add('btn', 'btn-dark')
                btnNo.textContent = 'Нет'
                btnNo.setAttribute('data-bs-dismiss', 'modal')
                footer.appendChild(btnNo)

                const btnYes = document.createElement('button')
                btnYes.type = 'button'
                btnYes.classList.add('btn', 'btn-danger')
                btnYes.textContent = 'Да'
                btnYes.onclick = () => {
                    if (this.confirmCallback) {
                        this.confirmCallback()
                    }
                    this.messageModal.hide()
                }
                footer.appendChild(btnYes)

                break
            
            default:
                modalHeader.classList.add('bg-primary', 'text-white')
                document.getElementById('messageModalLabel').textContent = 'Информация';
        }

        this.messageModal.show()
    }

    showFlashMessage() {
        const flashData = document.getElementById('flash-data')
        if (flashData) {
            try {
                const messages = JSON.parse(flashData.dataset.messages || '[]')
                if (messages.length > 0) {
                    // Проверяем категорию первого сообщения
                    const firstCategory = messages[0][0]
                    
                    // Если это ошибки валидации (может быть несколько), собираем их все
                    if (firstCategory === 'danger' && messages.length > 1) {
                        const errorMessages = messages.map(msg => msg[1]).join('\n')
                        this.showMessage(errorMessages, firstCategory)
                    } else {
                        // Для остальных случаев показываем последнее сообщение
                        const [category, message] = messages[messages.length - 1]
                        this.showMessage(message, category)
                    }
                }
            }
            catch (e) {
                console.error('Flash error', e)
            }
        }
    }

    confirm(msg, callback) {
        this.confirmCallback = callback
        this.showMessage(msg, 'confirm')
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.ModalManager = new ModalManager()
    window.ModalManager.showFlashMessage()

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.dataset.userId
            const userName = this.dataset.userName

            window.ModalManager.confirm(
                `Вы уверены, что хотите удалить ${userName}?`, () => {
                    const form = document.createElement('form')
                    form.method = 'POST'
                    form.action = `/delete/${userId}`
                    document.body.appendChild(form)
                    form.submit()
                }
            )
        })
    })
})