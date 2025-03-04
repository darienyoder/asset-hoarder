import requests
import mysql.connector
import hashlib

def generate_unique_hash(image_id, author, api_name):
    hash_input = f"{image_id}-{author}-{api_name}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def get_api_key(api_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT APIKey FROM API WHERE Name = %s", (api_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result['APIKey'] if result else None

def insert_asset(reference_hash, name, type_, storage_location):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Asset (ReferenceHash, Name, Type, StorageLocation) VALUES (%s, %s, %s, %s)", 
                   (reference_hash, name, type_, storage_location))
    conn.commit()
    cursor.close()
    conn.close()

def insert_image_asset(reference_hash, width, height):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ImageAsset (ReferenceHash, Width, Height) VALUES (%s, %s, %s)", 
                   (reference_hash, width, height))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_and_store_pixabay_images():
    api_key = get_api_key("Pixabay")
    if not api_key:
        print("Pixabay API key not found in the database.")
        return

    url = f"https://pixabay.com/api/?key={api_key}&image_type=photo&per_page=30"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        images = data.get("hits", [])
        for image in images:
            reference_hash = generate_unique_hash(str(image['id']), image['user'], "Pixabay")
            name = f"Pixabay_{image['id']}"
            type_ = 'image'
            storage_location = image['largeImageURL']
            width = image['imageWidth']
            height = image['imageHeight']

            insert_asset(reference_hash, name, type_, storage_location)
            insert_image_asset(reference_hash, width, height)

            print(f"Saved Image: ID={image['id']} Author={image['user']} Width={width} Height={height}")
    else:
        print(f"Failed to fetch Pixabay images. Status code: {response.status_code}")

if __name__ == '__main__':
    fetch_and_store_pixabay_images()
