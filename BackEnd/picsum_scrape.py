import requests
import mysql.connector
from flask import Flask

import hashlib

def generate_unique_hash(image_id, author, api_name):
    # Create a string by combining the image id, author, and the API name
    hash_input = f"{image_id}-{author}-{api_name}"
    
    # Generate a SHA-256 hash of the input string
    unique_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    return unique_hash


app = Flask(__name__)

db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

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
                reference_hash = generate_unique_hash(image['id'], image['author'], "PicSum")
                name = "PicSum" + image['id']  # Author of the image
                type_ = 'image'  # Type for image assets
                storage_location = image['download_url']

                # Insert asset record
                insert_asset(reference_hash, name, type_, storage_location)

                # Insert image asset (width and height are part of the image data)
                width = image['width']
                height = image['height']
                insert_image_asset(reference_hash, width, height)
                print(f"Saved Image: ID={image['id']} Author={image['author']} Width={width} Height={height} Hash={reference_hash}")

            page += 1
        else:
            print(f"Failed to fetch data for page {page}, status code {response.status_code}")
            break

@app.route('/')
def index():
    fetch_and_store_images()
    return "Data has been fetched and stored in the database!"

if __name__ == '__main__':
    app.run(debug=True)
