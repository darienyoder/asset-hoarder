#The Purpose of this file is to define the available actions that the API (this) can perform on the SQL Database
from flask import Flask, jsonify, request, render_template, session, send_file, after_this_request
from flask_cors import CORS
import requests
import mysql.connector
import hashlib
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv
import socket
import base64
import subprocess

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'devsecretkey').encode()

# Enables CORS to allow the frontend pages to access the backend data
CORS(app)

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
# SSH_SERVER_IP_ADDRESS="111.111.111.11"
# SSH_SERVER_PORT="11"
# changing user and pass for your own
# changing server ip and port for servers

# This is going to be broken

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
        database = db_config['database'],
        )

# Helper functions for database interactions
def get_db_connection():
    if socket.gethostname() == 'capstone1.cs.kent.edu':
        return mysql.connector.connect(**db_config)
    else:
        return get_ssh_db_connection()

# Main Page
@app.route('/')
def index():
    return render_template('main.html')

# get by each by type but use Asset.Id to have common reference id for user saving
# got rid of by asset types, use this to filter maybe, can revert if needed
@app.route('/assets', methods=['GET'])
def get_assets():
    tag = request.args.get('tag')

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
        ,t.Tag
    FROM ImageAsset AS ia
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = ia.ReferenceHash
    JOIN Asset AS a
        ON a.ReferenceHash = ia.ReferenceHash
    WHERE 0=0
    """
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    image_assets = cursor.fetchall()

    query = """
    SELECT
        a.Id
        ,a.StorageLocation
        ,aa.ReferenceHash
        ,aa.Duration
        ,t.Tag
    FROM AudioAsset AS aa
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = aa.ReferenceHash
    JOIN Asset AS a
        ON a.ReferenceHash = aa.ReferenceHash
    WHERE 0=0
    """
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    audio_assets = cursor.fetchall()

    query = """
    SELECT
        a.Id
        ,a.StorageLocation
        ,va.ReferenceHash
        ,va.Width
        ,va.Height
        ,va.Duration
        ,t.Tag
    FROM VideoAsset AS va
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = va.ReferenceHash
    JOIN Asset AS a
        ON a.ReferenceHash = va.ReferenceHash
    WHERE 0=0
    """
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'tag': tag})
    video_assets = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({'imageAssets': image_assets, 'audioAssets': audio_assets, 'videoAssets': video_assets}), 200

@app.route('/random_assets', methods=['GET'])
def get_random_assets():
    tag = request.args.get('tag')  # Optional filter by tag

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Base query to select all assets
    query = """
    SELECT Id, ReferenceHash, Name, Type, StorageLocation
    FROM Asset
    """

    # If a tag is specified, add it to the query filter
    if tag:
        query += " WHERE Type = %(tag)s"

    # Add random ordering
    query += " ORDER BY RAND()"

    # Execute the query
    cursor.execute(query, {'tag': tag})
    assets = cursor.fetchall()

    cursor.close()
    conn.close()

    if not assets:
        return 'No assets found', 404

    return jsonify({'assets': assets}), 200

@app.route('/create_account', methods=['POST'])
def post_create_account():
    username = request.form['username']
    password = request.form['password']

    if username is None or password is None:
        return 'enter username and password', 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        u.*
    FROM User AS u
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

# username and password will not be passed over url, just for testing, change with form.
@app.route('/login', methods=['POST'])
def get_login():
    username = request.form['username']
    password = request.form['password']
    #username = request.args.get('username')
    #password = request.args.get('password')

    if username is None or password is None:
        return 'enter username and password', 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        u.*
    FROM User AS u
    WHERE 0=0
    AND u.Username = %(username)s
    """
    cursor.execute(query, {'username': username})

    user = cursor.fetchone()
    if cursor.rowcount < 1:
        return 'wrong username or password', 400

    stringified_salt = user['PasswordSalt']
    salt = base64.b64decode(stringified_salt.encode())
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()

    cursor.close()
    conn.close()

    if hashed_password == user['HashedPassword']:
        session['userId'] = user['Id']
        return 'successful login', 200
    else:
        return 'wrong username or password', 400

@app.route('/logout', methods=['GET'])
def get_logout():
    if 'userId' not in session:
        return 'user not logged in', 400
    session.pop('userId')
    return 'successfully logged out', 200

@app.route('/user_toggle_save_asset/<int:asset_id>', methods=['POST'])
def post_user_toggle_save_asset(asset_id):
    if 'userId' not in session:
        return 'user not logged in', 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        a.*
    FROM Asset AS a
    WHERE 0=0
    AND a.Id = %(asset_id)s
    """
    cursor.execute(query, {'asset_id': asset_id})
    asset = cursor.fetchone()
    if cursor.rowcount < 1:
        return 'no asset found', 400
    cursor.fetchall()

    query = """
    SELECT
        *
    FROM UserSavedAssets AS usa
    WHERE 0=0
    AND usa.UserId = %(User_Id)s
    AND usa.ReferenceHash = %(Reference_Hash)s
    """
    cursor.execute(query, {'User_Id': session['userId'], 'Reference_Hash': asset['ReferenceHash']})
    cursor.fetchall()
    if cursor.rowcount > 0:
        query = """
        DELETE
        FROM UserSavedAssets AS usa
        WHERE 0=0
        AND usa.UserId = %(User_Id)s
        AND usa.ReferenceHash = %(Reference_Hash)s
        """
        try:
            cursor.execute(query, {'User_Id': session['userId'], 'Reference_Hash': asset['ReferenceHash']})
            conn.commit()
        except:
            return 'error unsaving asset', 500
        cursor.close()
        conn.close()
        return 'asset unsaved from user', 200
    else:
        query = """
        INSERT INTO UserSavedAssets (UserId, ReferenceHash)
        VALUES (%(User_Id)s, %(Reference_Hash)s)
        """
        try:
            cursor.execute(query, {'User_Id': session['userId'], 'Reference_Hash': asset['ReferenceHash']})
            conn.commit()
        except:
            return 'error saving asset', 500
        cursor.close()
        conn.close()
        return 'asset saved to user', 200

@app.route('/user_saved_assets', methods=['GET'])
def get_user_saved_assets():
    if 'userId' not in session:
        return 'user not logged in', 400

    tag = request.args.get('tag')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT
        a.Id
        ,a.StorageLocation
        ,ia.ReferenceHash
        ,ia.Width
        ,ia.Height
        ,t.Tag
    FROM ImageAsset AS ia
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = ia.ReferenceHash
    JOIN Asset AS a
        ON a.ReferenceHash = ia.ReferenceHash
    JOIN UserSavedAssets AS usa
        ON usa.ReferenceHash = ia.ReferenceHash
    WHERE 0=0
    AND usa.UserId = %(User_Id)s
    """
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'User_Id': session['userId'], 'tag': tag})
    image_assets = cursor.fetchall()

    query = """
    SELECT
        a.Id
        ,a.StorageLocation
        ,aa.ReferenceHash
        ,aa.Duration
        ,t.Tag
    FROM AudioAsset AS aa
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = aa.ReferenceHash
    JOIN Asset AS a
        ON a.ReferenceHash = aa.ReferenceHash
    JOIN UserSavedAssets AS usa
        ON usa.ReferenceHash = aa.ReferenceHash
    WHERE 0=0
    AND usa.UserId = %(User_Id)s
    """
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'User_Id': session['userId'], 'tag': tag})
    audio_assets = cursor.fetchall()

    query = """
    SELECT
        a.Id
        ,a.StorageLocation
        ,va.ReferenceHash
        ,va.Width
        ,va.Height
        ,va.Duration
        ,t.Tag
    FROM VideoAsset AS va
    LEFT JOIN Tags AS t
        ON t.ReferenceHash = va.ReferenceHash
    JOIN Asset AS a
        ON a.ReferenceHash = va.ReferenceHash
    JOIN UserSavedAssets AS usa
        ON usa.ReferenceHash = va.ReferenceHash
    WHERE 0=0
    AND usa.UserId = %(User_Id)s
    """
    if tag is not None:
        query += "AND t.Tag = %(tag)s"
    cursor.execute(query, {'User_Id': session['userId'], 'tag': tag})
    video_assets = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({'imageAssets': image_assets, 'audioAssets': audio_assets, 'videoAssets': video_assets}), 200

@app.route('/download/<int:asset_id>', methods=['GET'])
def download_asset(asset_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT StorageLocation
        FROM Asset
        WHERE id=""" + str(asset_id)
        cursor.execute(query)
        assets = cursor.fetchall()
        url = ""

        if assets:
            url = assets[0]["StorageLocation"]

        response = requests.get(url)
    except Exception as e:
        return print(f"Error querying database: {e}")

    file_path = "download/" + str(asset_id)

    if response.status_code == 200:
        try:
            os.makedirs("download/", exist_ok=True)
            with open(file_path, 'wb') as file:
                file.write(response.content)
        except Exception as e:
            return print(f"Error Writing file to server: {e}")

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing or closing downloaded file: {e}")
            return response

        downloadname = assets[0]["StorageLocation"].split("/")[-1]
        if not ("." in downloadname):
            downloadname += ".png"

        return send_file(file_path, as_attachment=True, download_name=downloadname)
    else:
        return "Failed to download asset"

@app.route('/fetch-api', methods=['GET'])
def fetch_all():
    result = subprocess.run(['python3', '../AssetCollectionScripts/fetch_mega_script.py', '--all'])
    if result.returncode == 0:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'error': 'Failed to start subprocess'}), 500


@app.route('/fetch-api/<string:api>', methods=['GET'])
def fetch_specific(api):
    # Validate if the api argument is valid
    valid_apis = ['picsum', 'unsplash', 'pixabay', 'pexels', 'freesound']
    
    if api.lower() not in valid_apis:
        return jsonify({'error': 'API not found'}), 404

    result = subprocess.run(['python3', '../AssetCollectionScripts/fetch_mega_script.py', f'--{api.lower()}'])
    if result.returncode == 0:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'error': 'Failed to start subprocess'}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
