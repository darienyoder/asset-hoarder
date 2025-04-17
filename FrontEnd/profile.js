
function toggle_profile_pane()
{
    if (document.getElementById("profile-pane").classList.contains("selected"))
        hide_profile();
    else
        show_profile();
}

function show_profile()
{
    document.getElementById("profile-pane").classList.add("selected");
    document.getElementById("profile-icon").classList.add("selected");

    document.getElementById("searchbar").blur()
}

function hide_profile()
{
    document.getElementById("profile-pane").classList.remove("selected");
    document.getElementById("profile-icon").classList.remove("selected");
    
    if (!gallery_open)
        document.getElementById("searchbar").focus()
}

function set_profile_tab( tabIndex )
{
    for (var tab in document.getElementById("profile-wrapper").children)
    {
        if (tab == tabIndex)
            document.getElementById("profile-wrapper").children[tab].classList.add("selected");
        else
            document.getElementById("profile-wrapper").children[tab].classList.remove("selected");
    }
}

function passConfirm() {
    if ((document.getElementById("new-pass").value ==
        document.getElementById("new-pass-rep").value) && 
        (document.getElementById("new-pass-rep").value != "") &&
        (document.getElementById("new-pass-rep").value != null)) {
            document.getElementById("pass-match-output").style.color = "#06402b";
            document.getElementById("pass-match-output").innerHTML = "&#x2714; Passwords match!"
    } else {
        document.getElementById("pass-match-output").style.color = "#8b0000";
        document.getElementById("pass-match-output").innerHTML = "&#x2716; Passwords do not match or are not valid."
    }
}

function emailConfirm() {
    if (/^([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-z]{2,})$/.test(document.getElementById("c_email").value)) {
            document.getElementById("checkEmail").style.color = "#06402b";
            document.getElementById("checkEmail").innerHTML = "&#x2714; Valid email!"
    } else {
        document.getElementById("checkEmail").style.color = "#8b0000";
        document.getElementById("checkEmail").innerHTML = "&#x2716; Please enter a valid email."
    }
}