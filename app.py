import time
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import jwt
from forms import TutorApplicationForm, ManagementApplicationForm
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import credentials, firestore, initialize_app, firestore
from datetime import datetime
import os
import pyrebase
from zoom_client import ZoomClient
from meeting_tools import handle_datetime, get_meeting_lists
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_xsecret_key'


if os.getenv('ENVIRONMENT') == 'prod':
    cred = credentials.ApplicationDefault()
else:
    cred = credentials.Certificate("key.json")  

initialize_app(cred)

config = {
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "projectId": os.getenv("FIREBASE_PROJECT_ID"),
  "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.getenv("FIREBASE_APP_ID"),
  "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

firebase = pyrebase.initialize_app(config)
db = firestore.client()

auth = firebase.auth()

ZOOM_ACCOUNT_ID = os.environ.get('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET')
ZOOM_SDK_ID = os.environ.get('ZOOM_SDK_ID')
ZOOM_SDK_SECRET = os.environ.get('ZOOM_SDK_SECRET')
client = ZoomClient(account_id=ZOOM_ACCOUNT_ID, client_id=ZOOM_CLIENT_ID, client_secret=ZOOM_CLIENT_SECRET, time_delta=90)



@app.context_processor
def inject_user():
    return dict(logged_In=True)

@app.route('/')
def index(): 
    return render_template('home.html')  


@app.route('/home')
def home():
    return render_template('home.html')  


@app.route('/gallery')
def gallery():
    
    if session.get("is_logged_in", False):
        return render_template('gallery.html') 
        
    return redirect(url_for('login'))


@app.route('/subject')
def subject():

    if session.get("is_logged_in", False):
        return render_template('subject.html')  
    return redirect(url_for('login'))

@app.route('/careers')
def careers():
    # print(session)

    if session.get("is_logged_in", False):
        return render_template('careers.html')  
    return redirect(url_for('login'))

@app.route('/management_vacancies')
def management_vacancies():

    if session.get("is_logged_in", False):
        return render_template('management_vacancies.html')  
    return redirect(url_for('login'))

@app.route('/tutoring_vacancies', methods=['GET', 'POST'])
def tutoring_vacancies():
    form = TutorApplicationForm()  # Create an instance of the form
    if session.get("is_logged_in", False):
        if form.validate_on_submit():
            # Handle form submission
            flash('Application submitted successfully!', 'success')
            return redirect('/success')
        return render_template('tutoring_vacancies.html', form=form) 
    return redirect(url_for('login'))


@app.route('/apply_management', methods=['GET', 'POST'])
def apply_management():
    role = request.args.get('role', '')  
    # print(role)

    form = ManagementApplicationForm()  # Create an instance of the form
    if session.get("is_logged_in", False):
        if form.validate_on_submit():
            # Handle form submission
            flash('Application submitted successfully!', 'success')
            return redirect('/success')
        return render_template('apply_management.html', form=form ,role=role) 
    return redirect(url_for('login'))

@app.route('/live_lesson')
def live_lesson():
    if session.get("is_logged_in", False):
        resp_list = client.get_meetings()
        meetings_list =  get_meeting_lists(resp_list)

        return render_template('live-lesson.html', meetings=meetings_list)  
    return redirect(url_for("login"))

@app.route('/recorded_lesson')
def recorded_lesson():
    if session.get("is_logged_in", False):
        return render_template('recorded-lesson.html')  
    return redirect(url_for("login"))


def generate_signature(meeting_number):
   # 30 seconds before current time
    iat = int(time.time()) - 30  # Convert to SECONDS
    exp = iat + (60 * 60 * 2)  
    token_exp = exp + (60 * 60 * 1000)  # Token expiry (in mill
    signature = jwt.encode(
        headers={
        "alg": "HS256",
        "typ": "JWT"
        },
    payload={
        'appKey': ZOOM_SDK_ID,
        'mn': meeting_number,
        'iat': iat,      # Issued at (SECONDS)
        'exp': exp,      # Expiry (SECONDS)
        'tokenExp': token_exp,  # Token Expiry (SECONDS)
        "role": 0,
    }, key=ZOOM_SDK_SECRET, algorithm='HS256')


    return signature


@app.route('/get_meeting/<int:meetingId>')
def get_meeting(meetingId):
    signature = generate_signature(meetingId)  # Role 0 for attendees
    return render_template('zoom_meeting.html', meeting_id=meetingId, signature=signature, sdk_key=ZOOM_SDK_ID)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return render_template("register.html", error="Email and password required")
        
        try:
           
            user = auth.create_user_with_email_and_password(email, password)
            # print(f"we have created {user}")

            email = data.get("email")
            name = data.get("name")
            surname = data.get("surname")
            password = data.get("password")
        
            session["uid"] =  user["localId"]
            session["name"] = name
            session["surname"] = surname
            session["email"] = email
            session["is_logged_in"] = True
            # Save user data
            data = {
                "name": name,
                "email": email,
                "surname" : surname,
                "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            }
            print(" We're Enter the Database")
            try:
                db.collection("users").document(session["uid"]).set(data)
                print("Data successfully written to Firestore!")
            except Exception as e:
                print("Error writing to Firestore:", e)

            user = auth.sign_in_with_email_and_password(email, password)
      
            # return render_template("register.html", message="User registered successfully")
            return render_template("home.html", message="Login successful")
        
        except Exception as e:
            return render_template("register.html", error=str(e))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        data = request.form
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return render_template("login.html", error="Email and password required")
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)

            # Store session variables on successful login
            session["is_logged_in"] = True
            session['uid'] = user['localId']
            session["email"] = email
            # print(session['uid'])

            # Retrieve the document from Firestore
            doc_ref = db.collection('users').document(session['uid'])
            doc_snapshot = doc_ref.get()

            # Check if the document exists and extract user data
            if doc_snapshot.exists:
                doc_data = doc_snapshot.to_dict()
                # print("Document Data:", doc_data)  # Print all fields in the document
                
                # Store additional data in session
                session["name"] = doc_data.get("name")
                session["surname"] = doc_data.get("surname")
                session["last_logged_in"] = doc_data.get("last_logged_in")
            else:
                print("No such document!")
            
            # Store the entire user object in the session (optional)
            session['user'] = user

            # Redirect to the home page with a success message
            return render_template("home.html", message="Login successful")
        
        except Exception as e:
            print("Error during login:", e)
            return render_template("login.html", error="Invalid email or password")
    
    return render_template('login.html')




@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        try:
            # Send password reset email
            auth.send_password_reset_email(email)
            return render_template("reset_password_done.html")  # Show a page telling user to check their email
        except Exception as e:
            print("Error occurred: ", e)
            return render_template("reset_password.html", error="An error occurred. Please try again.")  # Show error on reset password page
    else:
        return render_template("reset_password.html")  # Show the password reset page

@app.route('/logout')
def logout():
    # Clear specific session variables
    session.pop("uid", None)
    session.pop("is_logged_in", None)
    session.pop("name", None)
    session.pop("surname", None)
    session.pop("email", None)

    # Optional: Clear the entire session
    # session.clear()

    print("User logged out successfully.")

    # Redirect to login page after logout
    # return render_template("login.html", message="Logout successful")
    return  redirect(url_for('home'))

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

