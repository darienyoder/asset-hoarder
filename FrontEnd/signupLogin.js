const openModalButtons = document.querySelectorAll('[data-signup-target]')
const closeModalButtons = document.querySelectorAll('[data-signup-close]')
const overlay = document.getElementById('signup-overlay')

openModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const signupModal = document.querySelector(button.dataset.signupTarget)
            // may need to fix above line a little
        openModal(modal)
    })
})

closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const signupModal = button.closest('signupModal')
            // may need to fix above line a little
        openModal(modal)
    })
})

function openModal(signupModal){
    if (signupModal == null) return
    signupModal.classList.add('active')
    overlay.classList.add('active')
}

function closeModal(signupModal){
    if (signupModal == null) return
    signupModal.classList.remove('active')
    overlay.classList.remove('active')
}
