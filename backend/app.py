# Importing required libs
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, app
from model import preprocess_img, predict_result, allowed_file
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
import datetime
from datetime import timedelta
import requests
import json
from werkzeug.utils import secure_filename
from google.cloud import storage
import os
from dotenv import load_dotenv


load_dotenv() # Load environment variables from .env file
app = Flask(__name__)  # Instantiating flask app 
app.secret_key = os.urandom(24)
app.config['MYSQL_HOST'] = os.environ.get("DB_HOST")
app.config['MYSQL_USER'] = os.environ.get("DB_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("DB_PASS")
app.config['MYSQL_DB'] = os.environ.get("DB_DB")
app.config['UPLOAD_FOLDER'] = 'path/temp'  # Define the folder where uploaded files will be stored
mysql = MySQL(app)
CORS(app)
bcrypt = Bcrypt(app)

@app.before_first_request  # runs before FIRST request (only once)
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1440)

# home route
@app.route("/")
def main():
    return render_template("home.html")

@app.route('/predict')
def predict():
    if 'username' in session:
        return render_template("index.html")
    else:
        msg = 'Please Log In First!'
        return render_template('login.html', msg = msg)

# Login route
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s' , (username, ))
        account = cursor.fetchone()
        db_password = account["password"]
        if bcrypt.check_password_hash(db_password, password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

# logout route 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Register Route 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, hashed_password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('login.html', msg = msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg = msg)


# Prediction route
@app.route('/prediction', methods=['POST', 'GET'])
def predict_image_file():
    try:
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            
                img = preprocess_img(file.stream)
                pred = predict_result(img)

                waste_classes = ["Sampah Organik", "Sampah Plastik", "Sampah Kayu", "Sampah Besi", "Non Recycle"]
                results = waste_classes[pred]
                search_string = ["Sampah Organik",  "Sampah Plastik", "Sampah Kayu", "Sampah Besi", "Pembuangan Sampah Anorganik"]
                search = search_string[pred]

                # Configure the Google Cloud Storage client
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'key/c23-pc679-df01f7c3fd14.json'
                storage_client = storage.Client()
                bucket_name = 'img_ecocycle'
                bucket = storage_client.get_bucket(bucket_name)
                blob = bucket.blob(os.path.join('uploads/', filename))
                blob.upload_from_filename(file_path) 
                image = f'https://storage.googleapis.com/img_ecocycle/uploads/{filename}'

                os.remove(file_path)

                user_id = session['id']
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO map_data (result, search, user_id, image) VALUES (%s, %s, %s,%s)", (results, search, user_id, image))
                mysql.connection.commit()
                cur.close()

                return render_template("result.html", predictions=results, search=search, filename=filename)
            
        if request.method == 'GET':       
            cur = mysql.connection.cursor()
            user_id = session['id']
            cur.execute("SELECT (result, search) FROM map_data WHERE user_id = %s", (user_id))
            data = cur.fetchall()
            cur.close()

            results = data[-1][0]
            return render_template("result.html", predictions=results, search=results)

    except Exception as e:
        error = "Mohon Masukan Gambar Terlebih Dahulu"  + str(e)
        return render_template("result.html", err=error)


# maps route
@app.route('/maps')
def maps():
    if request.method == 'GET':   
        cur = mysql.connection.cursor()
        user_id = session['id']
        cur.execute("SELECT search FROM map_data WHERE user_id = %s", (user_id,))
        data = cur.fetchall()
        cur.close()
        api_key=os.environ.get("API_KEY_MAPS")
        if data:
            search_akhir = data[-1][0]
        else:
            search_akhir = None
        return render_template("maps.html", search=search_akhir, api_key=api_key)

###################################################
#API
###################################################

@app.route('/api/login', methods =['GET', 'POST'])
def apiLogin():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        # validate input
        username = data.get('username')
        password = data.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s' , (username, ))
        account = cursor.fetchone()
        db_password = account["password"]
        if bcrypt.check_password_hash(db_password, password):
            session['loggedin'] = True
            session['username'] = account['username']
            session['password'] = account['password']
            msg = 'Logged in successfully !'
            return jsonify ({
                'account id' : account['id'], 
                'username': account['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=450),
                'cookies id': app.secret_key,
                'message': msg})
        else:
            msg = 'Incorrect username / password !'
            return jsonify ({
                'message': msg
            } )
        
    except Exception as e:
        return {
                "message": "Something went wrong!",
                "error": str(e),
                "data": None
        }, 500
        
# maps route
@app.route('/api/maps', methods =['GET', 'POST'])
def apiMaps():
        img = preprocess_img(request.files['file'].stream)
        pred = predict_result(img)
        waste_classes = ["Sampah Organik", "Sampah Plastik", "Sampah Kayu", "Sampah Besi", "Non Recycle"]
        results_ = waste_classes[pred]
        search_string = ["Sampah_Organik",  "Sampah_Plastik", "Sampah_Kayu", "Sampah_Besi", "Pembuangan_Sampah_Anorganik"]
        search = search_string[pred]
        
        json_data = request.form['data']  # Access the JSON data as a string
        # Parse the JSON data into a Python dictionary
        data = json.loads(json_data)
        # Extract latitude and longitude from the data
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        api_key = os.environ.get("API_KEY_MAPS")  # Replace with your own Google Maps API key
        query = search # The query to search for
        location = f'{latitude},{longitude}'  # The location to search around (latitude,longitude)
        # Make API request to the Places API
        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={location}&key={api_key}'
        response = requests.get(url)

        # Process the API response
        if response.status_code == 200:
            results_ = results_
            data = response.json()
            results = data.get('results', [])
            # Extract relevant information from the results
            places = []
            resultplaces = [
                {
                    'jenis sampah': results_,
                    'latitude': latitude,
                    'longitude': longitude,
                    'results':places,
                }
            ]
            for result in results:
                place = {
                    'name': result.get('name'),
                    'address': result.get('formatted_address'),
                    'rating': result.get('rating')
                }
                places.append(place)

            # Return the places as JSON
            return jsonify(resultplaces)
        else:
            # Handle API error
            return jsonify({'error': 'Failed to fetch places data'})

# Driver code
if __name__ == "__main__":
    app.run(port=9000, debug=True)

