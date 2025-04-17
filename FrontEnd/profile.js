
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

    document.getElementById("searchbar").blur();

    if (document.getElementById("profile-wrapper").children[2].classList.contains("selected"))
        update_profile_results();
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
        document.getElementById("pass-match-output").innerHTML = "&#x2716; Passwords do NOT match!"
    }
}

async function toggle_save_asset(id)
{
    try
    {
        const response = await fetch("/user_toggle_save_asset/" + id);
        if (!response.ok)
        {
            throw new Error(`Response status: ${response.status}`);
        }

        let json = await response.json();
    }
    catch (error)
    {
        console.error(error.message);
    }
} 