
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