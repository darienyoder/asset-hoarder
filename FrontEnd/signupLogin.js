// Modals made with help from YouTube: https://youtu.be/MBaw_6cPmAw

const openModalButtons = document.querySelectorAll('[data-modal-target]')
const closeModalButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')

// Signup:

openModalButtons.forEach(button => { 
    button.addEventListener('click', () => {
        const modal = document.querySelector(button.dataset.modalTarget)
        openModal(modal)
    })
})

overlay.addEventListener('click', () => {
    const modals = document.querySelectorAll('.signup.active')
    modals.forEach(modal => {
        closeModal(modal)
    })
})

closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.signup')
        closeModal(modal)
    })
})

// Login:

openModalButtons.forEach(button => { 
    button.addEventListener('click', () => {
        const modal = document.querySelector(button.dataset.modalTarget)
        openModal(modal)
    })
})

overlay.addEventListener('click', () => {
    const modals = document.querySelectorAll('.login.active')
    modals.forEach(modal => {
        closeModal(modal)
    })
})

closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.login')
            // may need to fix above line a little
        closeModal(modal)
    })
})

// Open/Close

function openModal(modal){
    if (modal == null) return
    modal.classList.add('active')
    overlay.classList.add('active')
}

function closeModal(modal){
    if (modal == null) return
    modal.classList.remove('active')
    overlay.classList.remove('active')
}

var passConfirm = function() {
    if ((document.getElementById("new-pass").value ==
        document.getElementById("new-pass-rep").value) && 
        (document.getElementById("new-pass-rep").value != "") &&
        (document.getElementById("new-pass-rep").value != null)) {
            document.getElementById("pass-match-output").style.color = "#00811f";
            document.getElementById("pass-match-output").innerHTML = "&#x2714; Passwords match!"
    } else {
        document.getElementById("pass-match-output").style.color = "#943824";
        document.getElementById("pass-match-output").innerHTML = "&#x2716; Passwords do NOT match!"
    }
}

var properPass = function() {
    if (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$/.test
        (document.getElementById("new-pass").value)){
        document.getElementById("passwordNotes").style.color = "#00811f";
        document.getElementById("passwordNotes").innerHTML = "Valid password!"
    }
    else {
        document.getElementById("passwordNotes").style.color = "#943824";
        document.getElementById("passwordNotes").innerHTML = 
        "Your password must be between 8 and 32 characters, contain a lowercase letter, uppercase letter, and a special character (@, $, !, %, *, ?, or &)."
    }
}

var properUser = function() {
    if (/^[a-zA-Z0-9_]{3,16}$/.test
        (document.getElementById("new-user").value)){
        document.getElementById("usernameNotes").style.color = "#00811f";
        document.getElementById("usernameNotes").innerHTML = "Valid username!"
    }
    else {
        document.getElementById("usernameNotes").style.color = "#943824";
        document.getElementById("usernameNotes").innerHTML = 
        "Your username must be at least 3 chararacters and only include letters, numbers, and underscores."
    }
}
