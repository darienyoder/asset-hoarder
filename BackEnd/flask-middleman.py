#The Purpose of this file is to define the available actions that the API (this) can perform on the SQL Database

from flask import Flask, jsonify, request, render_template
import requests
import mysql.connector
import hashlib
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

# Use when running flask app locally, uncomment in get_db_connection()
# Must make a .env file and have: 
# SSH_USERNAME="user"
# SSH_PASSWORD="pass"
# changing user and pass for your own
def get_ssh_db_connection():
    load_dotenv()
    tunnel = SSHTunnelForwarder(
    ('174.104.199.92', 28),
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
    # return get_ssh_db_connection()
    return mysql.connector.connect(**db_config)

# Main Page
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/data/assets', methods=['GET'])
def get_assets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Asset"
    cursor.execute(query)
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'assets': assets}), 200

@app.route('/data/image_assets', methods=['GET'])
def get_image_assets():
    tag = request.args.get('tag')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        a.*
    FROM ImageAsset AS a
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = a.ReferenceHash
    WHERE 0=0
    """
    if tag:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    image_assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'image_assets': image_assets}), 200

@app.route('/data/audio_assets', methods=['GET'])
def get_audio_assets():
    tag = request.args.get('tag')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        a.*,
        t.Tag
    FROM AudioAsset AS a
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = a.ReferenceHash
    WHERE 0=0
    """
    if tag:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    audio_assets = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({'audio_assets': audio_assets}), 200

@app.route('/data/video_assets', methods=['GET'])
def get_video_assets():
    tag = request.args.get('tag')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        a.*,
        t.Tag
    FROM VideoAsset AS a
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = a.ReferenceHash
    WHERE 0=0
    """
    if tag:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    print(cursor._executed)
    video_assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'video_assets': video_assets}), 200

# This IP address doesn't matter, because its a local only address :)
if __name__ == '__main__':
    app.run(host='192.168.50.230', port=5000)
