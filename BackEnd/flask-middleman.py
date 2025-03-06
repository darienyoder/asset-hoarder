#The Purpose of this file is to define the available actions that the API (this) can perform on the SQL Database

from flask import Flask, jsonify, request, render_template
import requests
import mysql.connector
import hashlib
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv
import socket
import base64

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

# Use when running flask app locally
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
    #We should probably hide the ip-address and the port in the dotenv
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
    if socket.gethostname() == 'asset-hoarder':
        return mysql.connector.connect(**db_config)
    else:
        return get_ssh_db_connection()

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
    if tag is not None:
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
    if tag is not None:
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
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    video_assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'video_assets': video_assets}), 200

# get for now to easily test, change to post later once form is set up
@app.route('/data/create_account', methods=['GET'])
def post_create_account():
    username = request.args.get('username')
    password = request.args.get('password')

    if username is None or password is None:
        return 'enter username and password', 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        u.*
    FROM User as u
    WHERE 0=0
    AND u.Username = %(username)s
    """
    cursor.execute(query, {'username': username})
    cursor.fetchall()
    if cursor.rowcount > 0:
        return 'user already exists', 400
    salt = os.urandom(16)
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    stringified_salt = base64.b64encode(salt).decode()
    query = """
    INSERT INTO User (Username, HashedPassword, PasswordSalt)
    VALUES (%(username)s, %(hashed_password)s, %(salt)s)
    """
    try:
        cursor.execute(query, {'username': username, 'hashed_password': hashed_password, 'salt': stringified_salt})
        conn.commit()
    except:
        return 'error creating account', 500
    cursor.close()
    conn.close()
    return 'succesfully created account', 200

# username and password will not be passed over url, just for testing, change with form
@app.route('/data/login', methods=['GET'])
def get_login():
    username = request.args.get('username')
    password = request.args.get('password')

    if username is None or password is None:
        return 'enter username and password', 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        u.*
    FROM User as u
    WHERE 0=0
    AND u.Username = %(username)s
    """
    cursor.execute(query, {'username': username})
    user = cursor.fetchone()
    if cursor.rowcount < 1:
        return 'wrong username or password', 400
    stringified_salt = user["PasswordSalt"]
    salt = base64.b64decode(stringified_salt.encode())
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    cursor.close()
    conn.close()
    if hashed_password == user["HashedPassword"]:
        return 'successful login', 200
    else:
        return 'wrong username or password', 400

if __name__ == '__main__':
    app.run(host='192.168.50.230', port=5000)
