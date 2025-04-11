import requests
from io import BytesIO
from PIL import Image
import numpy as np
import mysql.connector

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
    "Violet": "#7F00FF"  # fixed hex format
}

### --- DATABASE HELPERS --- ###
def get_db_connection():
    return mysql.connector.connect(**db_config)

def insert_asset_tag(reference_hash, tag):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO Tags (ReferenceHash, Tag) VALUES (%s, %s)"
    cursor.execute(query, (reference_hash, tag))
    conn.commit()
    cursor.close()
    conn.close()

def get_image_assets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT ReferenceHash, StorageLocation FROM Asset"
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
    for asset in assets:
        try:
            img = download_image(asset['StorageLocation'])
            avg_rgb = get_average_rgb(img)
            avg_hex = rgb_to_hex(avg_rgb)

            common_hex = closest_color(avg_hex, PREDEFINED_COLORS)

            # Format the tags as per your requirement
            ac_tag = f"AC={avg_hex}"
            cc_tag = f"CC={common_hex}"

            insert_asset_tag(asset['ReferenceHash'], ac_tag)
            insert_asset_tag(asset['ReferenceHash'], cc_tag)

            print(f"Tagged {asset['ReferenceHash']} as {ac_tag} and {cc_tag}")
        except Exception as e:
            print(f"Failed to process {asset['StorageLocation']}: {e}")

if __name__ == '__main__':
    tag_images_with_colors()
