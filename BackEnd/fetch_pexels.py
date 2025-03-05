import requests
import mysql.connector
import hashlib

def generate_unique_hash(image_url):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Ensure we got a valid response

        # Read image data
        image_data = response.content

        # Generate SHA-256 hash from image content
        unique_hash = hashlib.sha256(image_data).hexdigest()
        return unique_hash

    except requests.RequestException as e:
        print(f"Error fetching image: {e}")
        return None  # Return None if fetching fails


db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def get_pexels_api_key():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT APIKey FROM API WHERE Name = 'Pexels'")
    api_key = cursor.fetchone()
    cursor.close()
    conn.close()

    if api_key:
        return api_key['APIKey']
    return None

def insert_asset(reference_hash, name, type_, storage_location):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO Asset (ReferenceHash, Name, Type, StorageLocation) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (reference_hash, name, type_, storage_location))
    conn.commit()
    cursor.close()
    conn.close()

def insert_image_asset(reference_hash, width, height):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO ImageAsset (ReferenceHash, Width, Height) VALUES (%s, %s, %s)"
    cursor.execute(query, (reference_hash, width, height))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_and_store_images():
    api_key = get_pexels_api_key()
    if not api_key:
        print("Error: Pexels API key not found in database.")
        return

    headers = {
        "Authorization": api_key
    }

    base_url = "https://api.pexels.com/v1/curated?page={page}&per_page=50"
    page = 1

    while True:
        url = base_url.format(page=page)
        response = requests.get(url, headers=headers)

        for image in images:
            image_url = image['url']
            reference_hash = generate_unique_hash(image_url)

            if reference_hash: 
                name = "Pexels_" + image['id']
                type_ = 'image'
                storage_location = image_url
                width = image['width']
                height = image['height']
            
                if not asset_exists(reference_hash):
                    insert_asset(reference_hash, name, type_, storage_location)
                    insert_image_asset(reference_hash, width, height)
            
                print(f"Saved Image: ID={image['id']} Photographer={image['photographer']} Width={width} Height={height}")
            
            # Increment page number for next request
            page += 1
        else:
            print(f"Failed to fetch data from Pexels on page {page}, status code {response.status_code}")
            break

# Start fetching images when the script is run directly
if __name__ == '__main__':
    fetch_and_store_images()
