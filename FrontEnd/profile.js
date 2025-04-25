
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
    // Check that they're the same then check that they're valid
    if ((document.getElementById("new-pass").value ==
        document.getElementById("new-pass-rep").value) && 
        (document.getElementById("new-pass-rep").value != "") &&
        (document.getElementById("new-pass-rep").value != null)) {
            if(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$/
                .test(document.getElementById("new-pass").value)){
                    // Confirmation Text
                    document.getElementById("pass-match-output").style.color = "#06402b";
                    document.getElementById("pass-match-output").innerHTML = "&#x2714; Passwords match!"
                }
            else{
                document.getElementById("pass-match-output").style.color = "#8b0000";
                document.getElementById("pass-match-output").innerHTML = "&#x2716; Invalid password."
            }
            
    } else {
        document.getElementById("pass-match-output").style.color = "#8b0000";
        document.getElementById("pass-match-output").innerHTML = "&#x2716; Passwords do not match."
    }
}

function emailConfirm() {
    if (/^([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-z]{2,})$/.test(document.getElementById("c_username").value)) {
            document.getElementById("checkEmail").style.color = "#06402b";
            document.getElementById("checkEmail").innerHTML = "&#x2714; Valid email!"
    } else {
        document.getElementById("checkEmail").style.color = "#8b0000";
        document.getElementById("checkEmail").innerHTML = "&#x2716; Please enter a valid email."
    }
}

async function toggle_save_asset(id)
{
    try
    {
        const response = await fetch(`/user_toggle_save_asset/` + assetId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
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
