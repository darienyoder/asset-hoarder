#The Purpose of this file is to define the available actions that the API (this) can perform on the SQL Database
import mysql.connector
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv
import socket
import random
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import pickle

load_dotenv()

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': '127.0.0.1',
    'database': 'ASSETHOARDER'
}

def get_ssh_db_connection():
    tunnel = SSHTunnelForwarder(
    (os.getenv('SSH_SERVER_IP_ADDRESS')),
    ssh_username = os.getenv('SSH_USERNAME'),
    ssh_password = os.getenv('SSH_PASSWORD'),
    remote_bind_address = ('127.0.0.1', 3306)
    )
    tunnel.start()
    return mysql.connector.connect(
        user = db_config['user'],
        password = db_config['password'],
        host = db_config['host'],
        port = tunnel.local_bind_port,
        database = db_config['database'],
        )

# Helper functions for database interactions
def get_db_connection():
    if socket.gethostname() == 'capstone1.cs.kent.edu':
        return mysql.connector.connect(**db_config)
    else:
        return get_ssh_db_connection()
    
def categorize_images():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        a.Id
        ,a.Name
        ,a.StorageLocation
        ,ia.ReferenceHash
        ,ia.Width
        ,ia.Height
    FROM ImageAsset AS ia
    JOIN Asset AS a
        ON a.ReferenceHash = ia.ReferenceHash
    WHERE 0=0
    AND ia.ReferenceHash NOT IN (
        SELECT t.ReferenceHash FROM Tags AS t
    )
    """
    cursor.execute(query)
    image_assets = cursor.fetchall()
    image_assets_links = []
    for image_asset in image_assets:
        image_assets_links.append(image_asset['StorageLocation'])

    client = OpenAI()
    data = []

    for i in range(0):
        try:
            # Load your image
            image_path = image_assets[i]['StorageLocation']  # Provide the image path
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Generate a list of 20 keyword phrases separated by commas that describe this image. Include things like the content, the background, the mood, and the style but separate them by each phrase. Only give those phrases in your response."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_path,
                                "detail": "low"
                            },
                        },
                    ],
                }],
            )
            tags = response.choices[0].message.content.split(',')
            for tag in tags:
                data.append((image_assets[i]['ReferenceHash'], tag.strip()))
            print(i)
        except:
            print(f'failed {i}')

        

    query = "INSERT INTO Tags (ReferenceHash, Tag) VALUES (%s, %s)"
    cursor.executemany(query, data)
    conn.commit()

    cursor.close()
    conn.close()

def generate_tag_values():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "select * from Tags as t where t.TagVector is null"
    cursor.execute(query)
    tags = cursor.fetchall()
    data = []
    query = "UPDATE Tags SET TagVector = %s WHERE Id = %s"
    i = 0
    j = 0
    for tag in tags:
        if i == 1000:
            cursor.executemany(query, data)
            data.clear()
            conn.commit()
            i = 0
            j = j + 1
        vector = pickle.dumps(model.encode(tag['Tag']))
        data.append((vector, tag['Id']))
        i = i + 1
        print(i + (j * 1000))
    cursor.executemany(query, data)
    conn.commit()

    cursor.close()
    conn.close()
    
if __name__ == '__main__':
    generate_tag_values()