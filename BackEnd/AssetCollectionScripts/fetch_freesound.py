import requests
import mysql.connector
import hashlib

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

def get_db_connection():
    """Establishes and returns a database connection."""
    return mysql.connector.connect(**db_config)

def get_freesound_api_key():
    """Retrieves the Freesound API key from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT APIKey FROM API WHERE Name = 'Freesound'")
    api_key = cursor.fetchone()
    cursor.close()
    conn.close()
    return api_key['APIKey'] if api_key else None

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

def fetch_and_store_sounds():
    """Fetches sounds from Freesound API and stores them in the database."""
    api_key = get_freesound_api_key()
    if not api_key:
        print("Error: Freesound API key not found in the database.")
        return

    headers = {"Authorization": f"Token {api_key}"}
    search_url = f"https://freesound.org/apiv2/search/text/?query=ambient&format=json&page_size=10"

    response = requests.get(search_url, headers=headers)

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
        details_response = requests.get(sound_details_url, headers=headers)
        if details_response.status_code != 200:
            print(f"Failed to fetch sound details for ID {sound_id}")
            continue

        sound_details = details_response.json()
        
        # Extract metadata
        sound_url = f"https://freesound.org/apiv2/sounds/{sound_id}/download/?token={api_key}"
        reference_hash = generate_unique_hash(sound_url)

        if reference_hash and not asset_exists(reference_hash):
            name = f"Freesound_{sound_id}"
            type_ = 'audio'
            storage_location = sound_url
            duration = sound_details.get('duration', 0)
            bitrate = sound_details.get('bitrate', 0)  # Might be None
            sample_rate = sound_details.get('samplerate', 0)

            insert_asset(reference_hash, name, type_, storage_location)
            insert_audio_asset(reference_hash, duration, bitrate, sample_rate)

            print(f"Saved Audio: ID={sound_id}, Duration={duration}s, Bitrate={bitrate}bps, SampleRate={sample_rate}Hz")

# Start script execution
if __name__ == '__main__':
    fetch_and_store_sounds()
