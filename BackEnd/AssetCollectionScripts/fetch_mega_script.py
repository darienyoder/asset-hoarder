import requests
import mysql.connector
import hashlib
import argparse

db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

def get_db_connection():
    """Establishes and returns a database connection."""
    return mysql.connector.connect(**db_config)

def generate_unique_hash(file_url):
    """Generates a SHA-256 hash based on file content."""
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        return hashlib.sha256(response.content).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching file: {e}")
        return None

def asset_exists(reference_hash):
    """Checks if an asset with the given hash already exists in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM Asset WHERE ReferenceHash = %s"
    cursor.execute(query, (reference_hash,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    return exists

def insert_asset(reference_hash, name, type_, storage_location):
    """Inserts a new asset into the Asset table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO Asset (ReferenceHash, Name, Type, StorageLocation) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (reference_hash, name, type_, storage_location))
    conn.commit()
    cursor.close()
    conn.close()

def insert_audio_asset(reference_hash, duration, bitrate, sample_rate):
    """Inserts audio metadata into the AudioAsset table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO AudioAsset (ReferenceHash, Duration, Bitrate, SampleRate) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (reference_hash, duration, bitrate, sample_rate))
    conn.commit()
    cursor.close()
    conn.close()

def insert_image_asset(reference_hash, width, height):
    """Inserts image metadata into the ImageAsset table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO ImageAsset (ReferenceHash, Width, Height) VALUES (%s, %s, %s)"
    cursor.execute(query, (reference_hash, width, height))
    conn.commit()
    cursor.close()
    conn.close()

def get_api_key(api_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT APIKey FROM API WHERE Name = %s", (api_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result['APIKey'] if result else None

def fetch_picsum():
    base_url = "https://picsum.photos/v2/list?page={page}&limit=100"
    page = 1
    while True:
        url = base_url.format(page=page)
        response = requests.get(url)

        if response.status_code == 200:
            images = response.json()
            if not images:  # If the API returns an empty list, stop the loop
                print(f"No more results returned on page {page}. Stopping.")
                break

            for image in images:
                reference_hash = generate_unique_hash(image['download_url'])
                name = ""  # Author of the image
                type_ = 'image'  # Type for image assets
                storage_location = image['download_url']

                # Insert asset record
                insert_asset(reference_hash, name, type_, storage_location)

                # Insert image asset (width and height are part of the image data)
                width = image['width']
                height = image['height']
                insert_image_asset(reference_hash, width, height)

                # Print details about the image saved
                print(f"Saved Image: ID={image['id']} Author={image['author']} Width={width} Height={height} Hash={reference_hash}")

            # Increment page number for next request
            page += 1
        else:
            print(f"Failed to fetch data for page {page}, status code {response.status_code}")
            break

def fetch_unsplash():
    api_key = get_api_key("Unsplash")
    if not api_key:
        print("Unsplash API key not found in the database.")
        return

    url = "https://api.unsplash.com/photos?per_page=30"
    headers = {"Authorization": f"Client-ID {api_key}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        images = response.json()
        for image in images:
            reference_hash = generate_unique_hash(image['urls']['full'])
            name = image['description']
            type_ = 'image'
            storage_location = image['urls']['full']
            width = image['width']
            height = image['height']

            insert_asset(reference_hash, name, type_, storage_location)
            insert_image_asset(reference_hash, width, height)

            print(f"Saved Image: ID={image['id']} Author={image['user']['name']} Width={width} Height={height}")
    else:
        print(f"Failed to fetch Unsplash images. Status code: {response.status_code}")

def fetch_pixabay():
    """Fetches images from Pixabay API and stores them in the database."""
    api_key = get_api_key("Pixabay")
    if not api_key:
        print("Error: Pixabay API key not found in the database.")
        return

    base_url = "https://pixabay.com/api/?key={api_key}&image_type=photo&per_page=30&page={page}"
    page = 1

    while True:
        url = base_url.format(api_key=api_key, page=page)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch data from Pixabay on page {page}, status code {response.status_code}")
            break

        data = response.json()
        images = data.get('hits', [])

        if not images:
            print(f"No more images found on page {page}. Stopping.")
            break

        for image in images:
            image_url = image.get('largeImageURL', '')
            if not image_url:
                continue  # Skip if no image URL is found

            reference_hash = generate_unique_hash(image_url)
            if reference_hash and not asset_exists(reference_hash):
                name = image['tags'].replace(",", "").title() # image['tags'] returns a string like "blossom, bloom, flower", which is changed to "Blossom Bloom Flower"
                type_ = 'image'
                storage_location = image_url
                width = image.get('imageWidth', 0)
                height = image.get('imageHeight', 0)
                photographer = image.get('user', 'Unknown')  # Pixabay uses "user" for uploader

                insert_asset(reference_hash, name, type_, storage_location)
                insert_image_asset(reference_hash, width, height)

                print(f"Saved Image: ID={image['id']} Photographer={photographer} Width={width} Height={height}")

        page += 1  # Move to the next page

def fetch_pexels():
    """Fetches images from Pexels API and stores them in the database."""
    api_key = get_api_key("Pexels")
    if not api_key:
        print("Error: Pexels API key not found in the database.")
        return

    headers = {"Authorization": api_key}
    base_url = "https://api.pexels.com/v1/curated?page={page}&per_page=50"
    page = 1

    while True:
        url = base_url.format(page=page)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch data from Pexels on page {page}, status code {response.status_code}")
            break

        data = response.json()
        images = data.get('photos', [])

        if not images:
            print(f"No more images found on page {page}. Stopping.")
            break

        for image in images:
            image_url = image['src']['original']  # Extract the high-quality image URL
            reference_hash = generate_unique_hash(image_url)

            if reference_hash and not asset_exists(reference_hash):
                name = image['alt']
                type_ = 'image'
                storage_location = image_url
                width = image['width']
                height = image['height']

                insert_asset(reference_hash, name, type_, storage_location)
                insert_image_asset(reference_hash, width, height)

                print(f"Saved Image: ID={image['id']} Photographer={image['photographer']} Width={width} Height={height}")

        page += 1  # Move to the next page

def fetch_freesound():
    """Fetches sounds from Freesound API and stores them in the database."""
    api_key = get_api_key("Freesound")
    if not api_key:
        print("Error: Freesound API key not found in the database.")
        return

    page = 1
    search_url = f"https://freesound.org/apiv2/search/text/?query=&format=json&page={page}&page_size=10&token={api_key}"

    response = requests.get(search_url)

    if response.status_code != 200:
        print(f"Failed to fetch data from Freesound, status code {response.status_code}")
        return

    data = response.json()
    sounds = data.get('results', [])

    if not sounds:
        print("No sounds found.")
        return

    for sound in sounds:
        sound_id = sound['id']
        sound_details_url = f"https://freesound.org/apiv2/sounds/{sound_id}/?token={api_key}"

        # Fetch sound details
        details_response = requests.get(sound_details_url)
        if details_response.status_code != 200:
            print(f"Failed to fetch sound details for ID {sound_id}")
            continue

        sound_details = details_response.json()

        sound_url = sound_details['url']
        reference_hash = generate_unique_hash(sound_url)

        if reference_hash and not asset_exists(reference_hash):
            name = sound_details.['name']
            type_ = 'audio'
            storage_location = sound_url
            duration = sound_details['duration']
            bitrate = sound_details['bitrate']  # Might be None
            sample_rate = sound_details['samplerate']

            insert_asset(reference_hash, name, type_, storage_location)
            insert_audio_asset(reference_hash, duration)

            print(f"Saved Audio: ID={sound_id}, Duration={duration}s, Bitrate={bitrate}bps, SampleRate={sample_rate}Hz")

if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser(description='Fetch data from different sources.')

    # Add arguments for each fetch function
    parser.add_argument('--picsum', action='store_true', help='Fetch from Picsum')
    parser.add_argument('--unsplash', action='store_true', help='Fetch from Unsplash')
    parser.add_argument('--pixabay', action='store_true', help='Fetch from Pixabay')
    parser.add_argument('--pexels', action='store_true', help='Fetch from Pexels')
    parser.add_argument('--freesound', action='store_true', help='Fetch from Freesound')
    
    # Add argument to fetch from all sources
    parser.add_argument('--all', action='store_true', help='Fetch from all sources')

    # Parse the arguments
    args = parser.parse_args()

    # If --all is specified, run all fetch functions
    if args.all:
        fetch_picsum()
        fetch_unsplash()
        fetch_pixabay()
        fetch_pexels()
        fetch_freesound()
    else:
        # Otherwise, run only the specified fetch functions
        if args.picsum:
            fetch_picsum()
        if args.unsplash:
            fetch_unsplash()
        if args.pixabay:
            fetch_pixabay()
        if args.pexels:
            fetch_pexels()
        if args.freesound:
            fetch_freesound()