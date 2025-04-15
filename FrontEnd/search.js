// Pressing enter will search regardless
// of what is currently selected
window.addEventListener("keydown", function(event) {
    if (event.key == "Enter" && !(gallery_open || document.getElementById("profile-pane").classList.contains("selected")))
        search();
    if (event.key == "Escape")
    {
        if (document.getElementById("profile-pane").classList.contains("selected"))
        {
            hide_profile();
        }
        else
        {
            if (gallery_open)
                hide_results();
            else if (document.getElementById("gallery").innerText != "")
                show_results();
        }
    }
    if (event.key == "`")
        toggle_profile_pane()
});

function show_results()
{
    document.getElementById("top-bar").classList.add("selected");
    document.getElementById("results-page").style.bottom = "0%";
    document.getElementById("top-bar-search").value = document.getElementById("searchbar").value
    gallery_open = true;

    document.getElementById("searchbar").blur();
}

function hide_results()
{
    document.getElementById("top-bar").classList.remove("selected");
    document.getElementById("results-page").style.bottom = "";
    gallery_open = false;

    document.getElementById("searchbar").focus();
}

var search_query = [];
var results = [];
var gallery_open = false;

// 1. Creates a link with GET attributes based on the selected filters
// 2. Fetches assets from that link and puts them in the results section
// 3. Scrolls to the top of the results section
async function search(random = false)
{

    document.getElementById("gallery").innerHTML = "";
    search_query = [];
    
    document.getElementById("loading-menu").style.display = "";
    show_results();

    let query = "";
    if (random && false) {
        query = "https://capstone1.cs.kent.edu/db/random_assets" + "?query=" + document.getElementById("main-searchbar").value
    } else {
        query = "https://capstone1.cs.kent.edu/db/search" + "?tag=" + document.getElementById("searchbar").value
    }
    
    // IMAGES
    if (document.getElementById("filter-wrapper").children[0].classList.contains("selected"))
    {
        query += "&isImage=true";
        
        // Type Filters
        // Ex. "type=photos+icons+textures"
        query += "&imgType=";
        for (const filter of document.getElementById("img-type-filters").children)
            if (filter.classList.contains("selected"))
            {
                query += filter.value + "+";
                search_query.push(filter.value);
            }
        if (query[query.length - 1] == "=")
        {
            query += "all";
        }
        if (query[query.length - 1] == "+")
        {
            query = query.substring(0, query.length - 1);
        }

        // Size Filters
        // Ex. "size=square+wide"
        query += "&size=";
        for (const filter of document.getElementById("img-size-filters").children)
            if (filter.classList.contains("selected"))
            {
                query += filter.value + "+";
                search_query.push(filter.value);
            }
        if (query[query.length - 1] == "=")
        {
            query += "all";
        }
        if (query[query.length - 1] == "+")
        {
            query = query.substring(0, query.length - 1);
        }

        // Color Filters
        // Ex. "size=orange+green+blue"
        query += "&color=";
        for (const filter of document.getElementById("img-color-filters").children)
            if (filter.classList.contains("selected"))
            {
                query += filter.value + "+";
                search_query.push(filter.value);
            }
        if (query[query.length - 1] == "=")
        {
            query += "all";
        }
        if (query[query.length - 1] == "+")
        {
            query = query.substring(0, query.length - 1);
        }
    }
    else
    {
        query += "&isImage=false"
    }

    // AUDIO
    if (document.getElementById("filter-wrapper").children[1].classList.contains("selected"))
    {
        query += "&isAudio=true";
        
        // Type Filters
        // Ex. "type=photos+icons+textures"
        query += "&audioType=";
        for (const filter of document.getElementById("audio-type-filters").children)
            if (filter.classList.contains("selected"))
                query += filter.value + "+";
        if (query[query.length - 1] == "=")
        {
            query += "all";
        }
        if (query[query.length - 1] == "+")
        {
            query = query.substring(0, query.length - 1);
        }

    }
    else
    {
        query += "&isAudio=false"
    }

    // Get results from API
    const response = await fetch(query);
    if (!response.ok)
    {
        throw new Error(`Response status: ${response.status}`);
    }

    let json = await response.json();
    results = json;

    // Temporary shuffling for testing purposes.
    // Delete this once the search filters work on the backend.
    if (!random) {
        results.sort((a, b) => Math.random() - 0.5 && (a.StorageLocation.includes("picsum") || a.Name.includes("Pexels") || a.Name.includes("Pixabay")));
    }

    // Update React app with results.
    update_results();

    document.getElementById("loading-menu").style.display = "none";

}