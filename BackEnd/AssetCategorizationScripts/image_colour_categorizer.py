import requests
from io import BytesIO
from PIL import Image
import numpy as np
import mysql.connector
from collections import Counter

# Database config
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

# Your specific color palette
PREDEFINED_COLORS = {
    "Red": "#FF0000",
    "Orange": "#FFA500",
    "Yellow": "#FFFF00",
    "Green": "#008000",
    "Blue": "#0000FF",
    "Violet": "#7F00FF",
    "White": "#FFFFFF",
    "Black": "#000000"
}

### --- DATABASE HELPERS --- ###
def get_db_connection():
    return mysql.connector.connect(**db_config)

def insert_colors(reference_hash, cc, ac):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE ImageAsset
        SET CommonColor = %s, ModeColor = %s
        WHERE ReferenceHash = %s
    """
    cursor.execute(query, (cc, ac, reference_hash))
    conn.commit()
    cursor.close()
    conn.close()

def get_image_assets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT ReferenceHash, StorageLocation FROM ImageAsset"
    cursor.execute(query)
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return assets

### --- IMAGE PROCESSING --- ###
def download_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert('RGB')
    return image

def get_average_rgb(image):
    np_img = np.array(image)
    avg_color = np_img.mean(axis=(0, 1))  # average over height & width
    return tuple(map(int, avg_color))  # (R, G, B)

def get_most_common_rgb(image):
    np_img = np.array(image)
    pixels = np_img.reshape(-1, 3)  # flatten to list of (R, G, B) tuples
    most_common = Counter(map(tuple, pixels)).most_common(1)[0][0]
    return most_common  # (R, G, B)

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def closest_color(avg_hex, color_dict):
    avg_rgb = hex_to_rgb(avg_hex)

    def distance(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2))

    # Find the closest color and return its hex (not name)
    return min(
        color_dict.values(),
        key=lambda color_hex: distance(avg_rgb, hex_to_rgb(color_hex))
    )

### --- MAIN FLOW --- ###
def tag_images_with_colors():
    assets = get_image_assets()
    failed_assets = []

    for asset in assets:
        try:
            # Skip assets that already have both CommonColor and AverageColor
            if asset.get('CommonColor') and asset.get('ModeColor'):
                print(f"Skipping {asset['ReferenceHash']}, already tagged.")
                continue

            img = download_image(asset['StorageLocation'])
            # avg_rgb = get_average_rgb(img)
            most_common_rgb = get_most_common_rgb(img)
            avg_hex = rgb_to_hex(most_common_rgb)


            common_hex = closest_color(avg_hex, PREDEFINED_COLORS)

            # Save directly to the ImageAsset table
            insert_colors(asset['ReferenceHash'], common_hex, avg_hex)

            print(f"Updated {asset['ReferenceHash']} with CommonColor={common_hex} and ModeColor={avg_hex}")
        except Exception as e:
            print(f"Failed to process {asset['StorageLocation']}: {e}")
            failed_assets.append({
                "ReferenceHash": asset['ReferenceHash'],
                "StorageLocation": asset['StorageLocation'],
                "Error": str(e)
            })

    if failed_assets:
        print("\n--- Failed Assets ---")
        for fail in failed_assets:
            print(f"{fail['ReferenceHash']} ({fail['StorageLocation']}): {fail['Error']}")

if __name__ == '__main__':
    tag_images_with_colors()
