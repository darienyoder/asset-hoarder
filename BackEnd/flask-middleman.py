#The Purpose of this file is to define the available actions that the API (this) can perform on the SQL Database

from flask import Flask, jsonify, request
import requests
import mysql.connector
import hashlib

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'dbuser',
    'password': 'dbpass',
    'host': 'localhost',
    'database': 'ASSETHOARDER'
}

# Helper functions for database interactions
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return "Welcome to the AssetHoarder API!"

@app.route('/assets', methods=['GET'])
def get_assets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Asset"
    cursor.execute(query)
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'assets': assets}), 200

@app.route('/image_assets', methods=['GET'])
def get_image_assets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM ImageAsset"
    cursor.execute(query)
    image_assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'image_assets': image_assets}), 200

if __name__ == '__main__':
    app.run(host='192.168.50.230', port=5000)
