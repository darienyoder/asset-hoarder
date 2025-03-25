
window.addEventListener("keydown", function(event) {
    if (event.key == "Enter")
        search();
});

var results = [];

async function search()
{
    let query = "https://assethoarder.net/db/assets"
    + "?query=" + document.getElementById("main-searchbar").value
    
    const response = await fetch("https://capstone1.cs.kent.edu/db/assets");
    if (!response.ok)
    {
        throw new Error(`Response status: ${response.status}`);
    }

    let json = await response.json();
    document.results = json.imageAssets;

    update_results();

    await new Promise(res => setTimeout(res, 10));

    document.getElementById('browse-page').style.display='block';
    document.getElementById('browse-anchor').scrollIntoView({ behavior: 'smooth'});
}