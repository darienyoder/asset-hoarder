from flask import Flask, jsonify, request, render_template, session, send_file, after_this_request, Response
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
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import json
import re

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'devsecretkey').encode()

# Enables CORS to allow the frontend pages to access the backend data
CORS(app)

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': '127.0.0.1',
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
#
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
        port = tunnel.local_bind_port,
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

@app.route('/search', methods=['GET'])
def search():
    if request.args.get('isImage') == "true":
        return get_image_assets()
    elif request.args.get('isAudio') == "true":
        return get_audio_assets()

@app.route('/image_assets', methods=['GET'])
def get_image_assets():
   input_tag = '' if request.args.get('tag') == None else request.args.get('tag')

   def chunked_image_assets(input_tag):
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
           ,t.TagVector
       FROM ImageAsset AS ia
       JOIN Asset AS a
           ON a.ReferenceHash = ia.ReferenceHash
       JOIN Tags AS t
           ON t.ReferenceHash = ia.ReferenceHash
       WHERE 0=0
       ORDER BY ia.ReferenceHash
       """
       cursor.execute(query)
       image_assets = cursor.fetchmany(1000)

       yield "["

       last_used_ref_hash = ''
       input_encoding = model.encode(input_tag)
       is_first_result = True
       while len(image_assets) != 0:
           added_asset = False
           for image_asset in image_assets:
               if added_asset and image_asset['ReferenceHash'] == last_used_ref_hash:
                   break
               if (last_used_ref_hash != image_asset['ReferenceHash']):
                   added_asset = False
               score = cosine_similarity([input_encoding], [pickle.loads(image_asset['TagVector'])])[0][0]
               if (score > 0.5 and not added_asset):
                   added_asset = True
                   return_asset = {'Id': image_asset['Id'], 'Name': image_asset['Name'], 'StorageLocation': image_asset['StorageLocation'], 'ReferenceHash': image_asset['ReferenceHash'], 'Width': image_asset['Width'], 'Height': image_asset['Height'], 'Tag': image_asset['Tag'], 'Score': str(score)}
                   if not is_first_result:
                       yield ","
                   yield "\n" + json.dumps(return_asset)
                   is_first_result = False
               last_used_ref_hash = image_asset['ReferenceHash']
           image_assets = cursor.fetchmany(1000)
       yield "\n]"
       


   return Response(chunked_image_assets(input_tag), content_type='application/json;charset=utf-8')

@app.route('/audio_assets', methods=['GET'])
def get_audio_assets():
   input_tag = '' if request.args.get('tag') == None else request.args.get('tag')

   def chunked_audio_assets(input_tag):
       conn = get_db_connection()
       cursor = conn.cursor(dictionary=True)

       query = """
       SELECT
           a.Id
           ,a.Name
           ,a.StorageLocation
           ,ia.ReferenceHash
           ,t.Tag
           ,t.TagVector
       FROM AudioAsset AS ia
       JOIN Asset AS a
           ON a.ReferenceHash = ia.ReferenceHash
       JOIN Tags AS t
           ON t.ReferenceHash = ia.ReferenceHash
       WHERE 0=0
       ORDER BY ia.ReferenceHash
       """
       cursor.execute(query)
       image_assets = cursor.fetchmany(1000)

       yield "["

       last_used_ref_hash = ''
       input_encoding = model.encode(input_tag)
       is_first_result = True
       while len(image_assets) != 0:
           added_asset = False
           for image_asset in image_assets:
               if added_asset and image_asset['ReferenceHash'] == last_used_ref_hash:
                   break
               if (last_used_ref_hash != image_asset['ReferenceHash']):
                   added_asset = False
               score = cosine_similarity([input_encoding], [pickle.loads(image_asset['TagVector'])])[0][0]
               if (score > 0.5 and not added_asset):
                   added_asset = True
                   return_asset = {'Id': image_asset['Id'], 'Name': image_asset['Name'], 'StorageLocation': image_asset['StorageLocation'], 'ReferenceHash': image_asset['ReferenceHash'], 'Tag': image_asset['Tag'], 'Score': str(score)}
                   if not is_first_result:
                       yield ","
                   yield "\n" + json.dumps(return_asset)
                   is_first_result = False
               last_used_ref_hash = image_asset['ReferenceHash']
           image_assets = cursor.fetchmany(1000)
       yield "\n]"
       


   return Response(chunked_audio_assets(input_tag), content_type='application/json;charset=utf-8')

# get by each by type but use Asset.Id to have common reference id for user saving
# got rid of by asset types, use this to filter maybe, can revert if needed
@app.route('/assets', methods=['GET'])
def get_assets():
    tag = request.args.get('tag')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    def fetch_assets(query, tag):
        if tag:
            query += " AND t.Tag = %(tag)s"
        cursor.execute(query, {'tag': tag})
        return cursor.fetchall()

    def fetch_tags_for_assets(asset_ids):
        if not asset_ids:
            return []
        
        query = """
        SELECT
            t.ReferenceHash,
            t.Tag
        FROM Tags AS t
        WHERE t.ReferenceHash IN (%s)
        """ % ','.join(['%s'] * len(asset_ids))  # Safely insert asset IDs into the query

        cursor.execute(query, asset_ids)
        return cursor.fetchall()

    image_query = """
    SELECT
        a.Id, a.Name, a.StorageLocation, ia.ReferenceHash, ia.Width, ia.Height
    FROM ImageAsset AS ia
    JOIN Asset AS a ON a.ReferenceHash = ia.ReferenceHash
    WHERE 0=0
    """
    audio_query = """
    SELECT
        a.Id, a.Name, a.StorageLocation, aa.ReferenceHash, aa.Duration
    FROM AudioAsset AS aa
    JOIN Asset AS a ON a.ReferenceHash = aa.ReferenceHash
    WHERE 0=0
    """
    video_query = """
    SELECT
        a.Id, a.Name, a.StorageLocation, va.ReferenceHash, va.Width, va.Height, va.Duration
    FROM VideoAsset AS va
    JOIN Asset AS a ON a.ReferenceHash = va.ReferenceHash
    WHERE 0=0
    """

    # Fetch asset data (no tags included)
    image_assets = fetch_assets(image_query, tag)
    audio_assets = fetch_assets(audio_query, tag)
    video_assets = fetch_assets(video_query, tag)

    # Extract all ReferenceHashes from assets to fetch tags
    asset_ids = [asset['ReferenceHash'] for asset in image_assets + audio_assets + video_assets]

    # Fetch tags for these assets
    tags = fetch_tags_for_assets(asset_ids)

    # Group tags by ReferenceHash
    tags_dict = {}
    for tag in tags:
        if tag['ReferenceHash'] not in tags_dict:
            tags_dict[tag['ReferenceHash']] = []
        tags_dict[tag['ReferenceHash']].append(tag['Tag'])

    # Add tags to assets
    def add_tags_to_assets(assets):
        for asset in assets:
            asset['Tags'] = tags_dict.get(asset['ReferenceHash'], [])
        return assets

    image_assets = add_tags_to_assets(image_assets)
    audio_assets = add_tags_to_assets(audio_assets)
    video_assets = add_tags_to_assets(video_assets)

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
        return jsonify('No assets found'), 404

    return jsonify({'assets': assets}), 200

@app.route('/create_account', methods=['POST'])
def post_create_account():
    username = request.form['username']
    password = request.form['password']

    if username is None or not username or password is None or not password:
        return jsonify('enter username and password'), 400

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
        return jsonify('username already exists'), 400
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
        return jsonify('error creating account'), 500
    cursor.close()
    conn.close()
    return jsonify('succesfully created account'), 200

# username and password will not be passed over url, just for testing, change with form.
@app.route('/login', methods=['POST'])
def post_login():
    username = request.form['username']
    password = request.form['password']
    #username = request.args.get('username')
    #password = request.args.get('password')

    if 'userId' in session:
        return jsonify('already logged in'), 400

    if username is None or not username or password is None or not password:
        return jsonify('enter username and password'), 400

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
        return jsonify('wrong username or password'), 400

    stringified_salt = user['PasswordSalt']
    salt = base64.b64decode(stringified_salt.encode())
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()

    cursor.close()
    conn.close()

    if hashed_password == user['HashedPassword']:
        session['userId'] = user['Id']
        return jsonify('successful login'), 200
    else:
        return jsonify('wrong username or password'), 400

@app.route('/logout', methods=['GET'])
def get_logout():
    if 'userId' not in session:
        return jsonify('user not logged in'), 400
    session.pop('userId')
    return jsonify('successfully logged out'), 200

@app.route('/delete_account', methods=['POST'])
def post_delete_account():
    if 'userId' not in session:
        return jsonify('user not logged in'), 400
    
    username = request.form['username']
    password = request.form['password']

    if username is None or not username or password is None or not password:
        return jsonify('enter username and password'), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        u.*
    FROM User AS u
    WHERE 0=0
    AND u.Id = %(id)s
    """
    cursor.execute(query, {'id': session['userId']})
    user = cursor.fetchone()

    # should not happen but just checking anyway
    if user is None:
        return jsonify('something went wrong'), 500
    
    if user['Username'] != username:
        return jsonify('username does not match current user'), 400
    cursor.fetchall()

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
        return jsonify('wrong username or password'), 400

    stringified_salt = user['PasswordSalt']
    salt = base64.b64decode(stringified_salt.encode())
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()

    cursor.fetchall()

    if hashed_password != user['HashedPassword']:
        return jsonify('wrong username or password'), 400
    
    
    query = """
    DELETE 
    FROM User
    WHERE 0=0
    AND Id = %(userId)s
    """
    cursor.execute(query, {'userId': user['Id']})
    deleted = cursor.rowcount > 0
    if not deleted:
        return jsonify('something went wrong'), 500

    conn.commit()
    cursor.close()
    conn.close()
    session.pop('userId')
    return jsonify('successfully deleted account and logged out'), 200
    

@app.route('/user_toggle_save_asset/<int:asset_id>', methods=['POST'])
def post_user_toggle_save_asset(asset_id):
    if 'userId' not in session:
        return jsonify('user not logged in'), 400

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
        return jsonify('no asset found'), 400
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
            return jsonify('error unsaving asset'), 500
        cursor.close()
        conn.close()
        return jsonify('asset unsaved from user'), 200
    else:
        query = """
        INSERT INTO UserSavedAssets (UserId, ReferenceHash)
        VALUES (%(User_Id)s, %(Reference_Hash)s)
        """
        try:
            cursor.execute(query, {'User_Id': session['userId'], 'Reference_Hash': asset['ReferenceHash']})
            conn.commit()
        except:
            return jsonify('error saving asset'), 500
        cursor.close()
        conn.close()
        return jsonify('asset saved to user'), 200

@app.route('/user_saved_assets', methods=['GET'])
def get_user_saved_assets():
    if 'userId' not in session:
        return jsonify('user not logged in'), 400

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
    # result = subprocess.run(['python3', 'AssetCollectionScripts/fetch_mega_script.py', '--all'])
    # This has been disabled for now until we work out admin accounts, we dont want every user to be able to run this
    # if result.returncode == 0:
    #     return jsonify({'status': 'success'}), 200
    # else:
    #     return jsonify({'error': 'Failed to start subprocess'}), 500
    return jsonify({'error': 'This has been disabled'}), 405


@app.route('/fetch-api/<string:api>', methods=['GET'])
def fetch_specific(api):
    # Validate if the api argument is valid
    # valid_apis = ['picsum', 'unsplash', 'pixabay', 'pexels', 'freesound']
    
    # if api.lower() not in valid_apis:
    #     return jsonify({'error': 'API not found'}), 404

    # result = subprocess.run(['python3', 'AssetCollectionScripts/fetch_mega_script.py', f'--{api.lower()}'])
    # if result.returncode == 0:
    #     return jsonify({'status': 'success'}), 200
    # else:
    #     return jsonify({'error': 'Failed to start subprocess'}), 500
    
    return jsonify({'error': 'This has been disabled'}), 405


@app.route('/cleanup', methods=['GET'])
def cleanup():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("DELETE FROM Asset WHERE Name LIKE 'PicSum%' OR Name LIKE 'Pexels%' OR Name LIKE 'Pixabay%'")

        cursor.execute("DELETE FROM ImageAsset WHERE NOT EXISTS (SELECT * FROM Asset WHERE ImageAsset.ReferenceHash = Asset.ReferenceHash)")
        cursor.execute("DELETE FROM AudioAsset WHERE NOT EXISTS (SELECT * FROM Asset WHERE AudioAsset.ReferenceHash = Asset.ReferenceHash)")
        cursor.execute("DELETE FROM VideoAsset WHERE NOT EXISTS (SELECT * FROM Asset WHERE VideoAsset.ReferenceHash = Asset.ReferenceHash)")
        cursor.execute("DELETE FROM Tags WHERE NOT EXISTS (SELECT * FROM Asset WHERE Tags.ReferenceHash = Asset.ReferenceHash)")

        conn.commit()
        return jsonify({
            'status': 'success',
            'message': 'Cleanup completed successfully'
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        })

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
