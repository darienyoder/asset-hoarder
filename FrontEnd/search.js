
// Pressing enter will search regardless
// of what is currently selected
window.addEventListener("keydown", function(event) {
    if (event.key == "Enter")
        search();
});

var results = [];

// 1. Creates a link with GET attributes based on the selected filters
// 2. Fetches assets from that link and puts them in the results section
// 3. Scrolls to the top of the results section
async function search(random = false)
{
    let query = ""
    if (random) {
        query = "https://capstone1.cs.kent.edu/db/random_assets"
    } else {
        query = "https://assethoarder.net/db/assets"
            + "?query=" + document.getElementById("main-searchbar").value
    }
    
    // IMAGES
    if (document.getElementById("content-filters").children[0].classList.contains("selected"))
    {
        query += "&isImage=true";
        
        // Type Filters
        // Ex. "type=photos+icons+textures"
        query += "&imgType=";
        for (const filter of document.getElementById("img-type-filters").children)
            if (filter.classList.contains("selected"))
                query += filter.value + "+";
        if (query[query.length - 1] == "=")
        {
            for (const filter of document.getElementById("img-type-filters").children)
                query += filter.value + "+";
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
                query += filter.value + "+";
        if (query[query.length - 1] == "=")
        {
            for (const filter of document.getElementById("img-size-filters").children)
                query += filter.value + "+";
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
                query += filter.value + "+";
        if (query[query.length - 1] == "=")
        {
            for (const filter of document.getElementById("img-color-filters").children)
                query += filter.value + "+";
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
    if (document.getElementById("content-filters").children[1].classList.contains("selected"))
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
                for (const filter of document.getElementById("audio-type-filters").children)
                    query += filter.value + "+";
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
    results = json.imageAssets;

    // Temporary shuffling for testing purposes.
    // Delete this once the search filters work on the backend.
    if (!random) {
        results.sort((a, b) => Math.random() - 0.5 && (a.StorageLocation.includes("picsum") || a.Name.includes("Pexels") || a.Name.includes("Pixabay")));
    }

    // Update React app with results.
    update_results();

    // Wait a frame to let the content load, then scroll down to results.
    // If the content isn't loaded, the page can't scroll all the way.
    await new Promise(res => setTimeout(res, 10));

    document.getElementById('browse-page').style.display = 'block';
    document.getElementById('browse-anchor').scrollIntoView({ behavior: 'smooth'});
}