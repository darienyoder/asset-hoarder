
var current_audio = -1;
var setting_time = false;
var hover_time_counter = 0;
var prev_width = 512;

function toggle_audio(new_audio)
{
    if (new_audio == current_audio)
    {
        document.getElementById("audio-player-" + current_audio).pause();
        // document.getElementById("play-button-" + new_audio).style = "";
        current_audio = -1;
    }
    else
    {
        if (current_audio != -1)
        {
            document.getElementById("audio-player-" + current_audio).pause();
            // document.getElementById("play-button-" + current_audio).style = "";
        }
        document.getElementById("audio-player-" + new_audio).play();
        // document.getElementById("play-button-" + new_audio).style.backgroundImage = "url(https://icon-library.com/images/pause-icon-transparent/pause-icon-transparent-8.jpg)";
        current_audio = new_audio;
    }
}

function Entry({ data })
{
    let asset = data;
    let asset_ID = asset.id;

    if (asset.type == "image")
    {
        let style_content = ".entry-" + asset_ID + `:hover > .image-preview {
            z-index: 10; ` + (asset.width > asset.height ? `
            width: calc(100% * ` + (asset.width / asset.height)  + `);
            ` : `width: 100%;
            height: calc(100% * ` + (asset.height / asset.width)  + `);`) + `
            transform: scale(1.1);
        }`;

        if (asset.height > asset.width)
        {
            style_content += ".entry-" + asset_ID + ` .download-button {
                aspect-ratio: 1;
                width: 30%;
                height: auto;
            }`;
        }

        return (
            <div className={"entry image-entry entry-" + asset_ID}>
                <div className="image-preview"
                    style={{ backgroundImage: `url(${asset.file}?w=${prev_width})` }}
                    loading="lazy">
                    <div className="entry-title">{asset.title}</div>
                    <a className="download-button" onClick={`toggle_save_asset('${asset.id}');`} href={`/db/download/${asset.id}`} download></a>
                </div>

                {/* Preload the image to ensure it's fetched as soon as possible */}
                <link rel="preload" href={`${asset.file}?w=${prev_width}`} as="image" />

                {/* Critical CSS for the image-entry styles */}
                <style>{style_content}</style>
            </div>

        );
    }
    else if (asset.type == "audio")
    {
        return (
            <div id={"entry-" + asset_ID} className="entry audio-entry" onMouseOver={(event) => toggle_audio(asset_ID)} onMouseOut={(event) => toggle_audio(asset_ID)}>
                <a id={"play-button-" + asset_ID} className={"audio-play-button"} href={`/db/download/${asset.id}`} download></a>
                <audio id={"audio-player-" + asset_ID}>
                    <source src={asset.file} type="audio/ogg" />
                </audio>

                <div className="entry-title" onMouseOver={(event) => setting_time = true} onMouseOut={(event) => setting_time = false}>
                    <div id={"media-progress-" + asset_ID} className="media-progress-bar">
                        <div className="media-progress-bar-tip"></div>
                    </div>
                    {asset.title}
                </div>
            </div>
        );
    }
}

function timer()
{
    if (current_audio != -1)
    {
        document.getElementById("media-progress-" + current_audio).style.width = (document.getElementById("audio-player-" + current_audio).currentTime / document.getElementById("audio-player-" + current_audio).duration * 100) + "%";
    }
}

var mouseX = 0.0;
var mouseY = 0.0;

window.addEventListener("mousemove", event => {

    if (mouseX == event.clientX && mouseY == event.clientY)
        hover_time_counter = -10;

    mouseX = event.clientX;
    mouseY = event.clientY;

    if (setting_time)
    {
        hover_time_counter += 1;

        if (hover_time_counter >= 5)
            document.getElementById("audio-player-" + current_audio).currentTime = (
                document.getElementById("audio-player-" + current_audio).duration
                * (event.clientX - document.getElementById("entry-" + current_audio).getBoundingClientRect().left)
                / (document.getElementById("entry-" + current_audio).getBoundingClientRect().right - document.getElementById("entry-" + current_audio).getBoundingClientRect().left)
            );
    }
    else
        hover_time_counter = 0;
});

var results_index = 0;

async function update_results(index = 0)
{
    try
    {
        results_index = index;
        document.getElementById("gallery-header").innerText = "";

        if (results.length == 0)
        {
            // document.getElementById("no-results").style.display = "";
        }
        else
        {
            var entry_list = [];
            // Do NOT load more than 15 assets at a time or your browser will crash
            for (var i = results_index; i < results.length; i++)
            {
                let entry = {
                    "type": results[i].Type,
                    "id": results[i].Id,
                    "file": results[i].StorageLocation,
                    "title": results[i].Name,
                };
                if (entry.type == "image")
                {
                    entry.width = results[i].Width;
                    entry.height = results[i].Height;
                }
                entry_list.push(<Entry data={entry} />)
            }
    
            const container = document.getElementById('gallery');
            const root = ReactDOM.createRoot(container);
            root.render(entry_list);

            document.getElementById("gallery-header").innerText = results.length + " results"
        }
    }
    catch (error)
    {
        console.error(error.message);
    }
}

setInterval(timer, 33);

async function update_profile_results()
{
    try
    {
        // Get results from API
        const response = await fetch("https://assethoarder.net/db/user_saved_assets");
        if (!response.ok)
        {
            throw new Error(`Response status: ${response.status}`);
        }

        let json = await response.json();
        let profile_results = json["imageAssets"].concat(json["audioAssets"]);

        document.getElementById("saved-gallery").innerHTML = "";

        if (profile_results.length == 0)
        {
            // document.getElementById("no-results").style.display = "";
        }
        else
        {
            var entry_list = [];
            // Do NOT load more than 15 assets at a time or your browser will crash
            for (var i = 0; i < profile_results.length; i++)
            {
                let entry = {
                    "type": profile_results[i].Type,
                    "id": profile_results[i].Id,
                    "file": profile_results[i].StorageLocation,
                    "title": profile_results[i].Name,
                };
                if (entry.type == "image")
                {
                    entry.width = profile_results[i].Width;
                    entry.height = profile_results[i].Height;
                }
                entry_list.push(<Entry data={entry} />)
            }
    
            const container = document.getElementById('saved-gallery');
            const root = ReactDOM.createRoot(container);
            root.render(entry_list);
        }
    }
    catch (error)
    {
        console.error(error.message);
    }
}