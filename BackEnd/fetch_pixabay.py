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

def get_pixabay_api_key():
    """Retrieves the Pixabay API key from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT APIKey FROM API WHERE Name = 'Pixabay'")
    api_key = cursor.fetchone()
    cursor.close()
    conn.close()
    return api_key['APIKey'] if api_key else None

def generate_unique_hash(image_url):
    """Generates a SHA-256 hash based on image content."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image_data = response.content
        return hashlib.sha256(image_data).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching image: {e}")
        return None  # Return None if fetching fails

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

def insert_image_asset(reference_hash, width, height):
    """Inserts image metadata into the ImageAsset table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO ImageAsset (ReferenceHash, Width, Height) VALUES (%s, %s, %s)"
    cursor.execute(query, (reference_hash, width, height))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_and_store_images():
    """Fetches images from Pixabay API and stores them in the database."""
    api_key = get_pixabay_api_key()
    if not api_key:
        print("Error: Pixabay API key not found in the database.")
        return

    headers = {"Authorization": api_key}
    base_url = "https://pixabay.com/api/?key={api_key}&image_type=photo&per_page=30"
    page = 1

    while True:
        url = base_url.format(page=page)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch data from Pixabay on page {page}, status code {response.status_code}")
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
                name = "Pixabay_" + str(image['id'])
                type_ = 'image'
                storage_location = image_url
                width = image['width']
                height = image['height']

                insert_asset(reference_hash, name, type_, storage_location)
                insert_image_asset(reference_hash, width, height)

                print(f"Saved Image: ID={image['id']} Photographer={image['photographer']} Width={width} Height={height}")

        page += 1  # Move to the next page

# Start the script when run directly
if __name__ == '__main__':
    fetch_and_store_images()
