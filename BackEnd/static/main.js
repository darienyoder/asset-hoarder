const test_assets = [
    {
        "type": "image",
        "file": "https://wallpapers.com/images/featured/cat-pictures-zc3gu0636kmldm04.jpg",
        "title": "The Orange",
        "width": 900,
        "height": 563,
    },
    {
        "type": "image",
        "file": "https://wallpaper-house.com/data/out/6/wallpaper2you_103955.jpg",
        "title": "Dinnertime",
        "width": 1920,
        "height": 1080,
    },
    {
        "type": "image",
        "file": "https://www.itl.cat/pngfile/big/47-478337_kitten-wallpapers-hd.jpg",
        "title": "Leo the Magnificent",
        "width": 1920,
        "height": 1200,
    },
    {
        "type": "image",
        "file": "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.kittyloaf.com%2Fwp-content%2Fuploads%2F2017%2F06%2FValentine_KittyLoaf_071417-375x375.png",
        "title": "Pancake",
        "width": 375,
        "height": 375,
    },


    {
        "type": "audio",
        "file": "https://static.wikia.nocookie.net/undertale/images/6/63/Another_Medium_music.ogg",
        "title": "Another Medium",
        "duration": 2*60+22,
    },
    {
        "type": "audio",
        "file": "https://static.wikia.nocookie.net/undertale/images/1/12/It%27s_Raining_Somewhere_Else_music.ogg",
        "title": "It's Raining Somewhere Else",
        "duration": 2*60+50,
    },
    {
        "type": "audio",
        "file": "https://static.wikia.nocookie.net/undertale/images/9/93/Waterfall_%28Soundtrack%29_music.ogg",
        "title": "Waterfall",
        "duration": 2*60+6,
    },
    {
        "type": "audio",
        "file": "https://ia902902.us.archive.org/31/items/01.smellsliketeenspirit/01.Smells%20Like%20Teen%20Spirit.mp3",
        "title": "Smells Like Team Spirit",
        "duration": 5*60+1,
    },
]

var current_audio = -1;
var setting_time = false;
var hover_time_counter = 0;

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

function Entry()
{
    let asset = test_assets[Math.floor(Math.random() * test_assets.length)]
    let asset_ID = Math.floor(Math.random() * 2147483000);

    if (asset.type == "image")
    {
        let style_content = ".entry-" + asset_ID + `:hover > .image-preview {
            z-index: 10;
            width: calc(100% * ` + (asset.width / asset.height)  + `);
            transform: scale(1.1);
        }`;

        return (
            <div className={"entry image-entry entry-" + asset_ID}>
                <div className="image-preview" style={{backgroundImage: "url(" + asset.file + ")"}}>
                    <div className="entry-title">{asset.title}</div>
                    <a className="download-button" href={asset.file} download></a>
                </div>
                <style>{style_content}</style>
            </div>
        );
    }
    else if (asset.type == "audio")
    {
        return (
            <div id={"entry-" + asset_ID} className="entry audio-entry" onMouseOver={(event) => toggle_audio(asset_ID)} onMouseOut={(event) => toggle_audio(asset_ID)}>
                <a id={"play-button-" + asset_ID} className={"audio-play-button"} href={asset.file} download></a>
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

function main()
{
    var entry_list = [];
    for (var i = 0; i < 100; i++)
        entry_list.push(<Entry />)

    const container = document.getElementById('browse-content');
    const root = ReactDOM.createRoot(container);
    root.render(entry_list);

    setInterval(timer, 33);
}
