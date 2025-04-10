
function toggle_profile_pane()
{
    document.getElementById("profile-pane").classList.toggle("selected");
}

function show_profile()
{
    document.getElementById("profile-pane").classList.add("selected");
}

function hide_profile()
{
    document.getElementById("profile-pane").classList.remove("selected");
}