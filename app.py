from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from forms import TutorApplicationForm, ManagementApplicationForm
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import pyrebase
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = 'your_secret_key'  

cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)


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

@app.context_processor
def inject_user():
    return dict(logged_In=True)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/home')
def home():
    print("We are in home page")
    if session.get("is_logged_in", False):
        return render_template('home.html')  # Subject page
    return redirect(url_for('login'))

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
    print(session)

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
    print(role)

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
        return render_template('live-lesson.html')  
    return redirect(url_for("login"))

@app.route('/recorded_lesson')
def recorded_lesson():
    if session.get("is_logged_in", False):
        return render_template('recorded-lesson.html')  
    return redirect(url_for("login"))

# @app.route('/logout')
# def logout():

#     # db.child("users").child(session["uid"]).update({"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")})
#     print(session)
#     session["is_logged_in"] = False
#     return redirect(url_for('login'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if request.method == 'POST':
#         if form.is_submitted():
#             email = form.email.data
#             name = form.name.data
#             surname = form.surname.data
#             password = form.password.data
#             user = auth.create_user(email=email, password=password)
       
        
#             print(user)
#             session["uid"] = user.uid
#             session["name"] = name
#             session["surname"] = surname
#             session["email"] = email
#             session["is_logged_in"] = True
#             # Save user data
#             data = {
#                 "name": name,
#                 "email": email,
#                 "surname" : surname,
#                 "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#             }
            
#             # Create user account
#             auth.create_user_with_email_and_password(email, password)
#             # Authenticate user
#             user = auth.sign_in_with_email_and_password(email, password)

#             try : 
#                 db.collection("users").document(session["uid"]).set(data)
 
#                 return redirect(url_for('home'))
#             except Exception as e:
#                 flash(f'Login successful!{e}', 'success')
                


#     return render_template('register.html', form=form)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             email = form.email.data
#             password = form.password.data


            
#             try : 

#             
#                 flash('Login successful!', 'success')
#                 return redirect(url_for('home'))
#             except Exception as e:
#                 flash(f'Login successful!{e}', 'success')
                
     

#     return render_template('login.html', form=form)

# # Route for password reset
# @app.route("/reset_password", methods=["GET", "POST"])
# def reset_password():
#     if request.method == "POST":
#         email = request.form["email"]
#         try:
            
#             auth.send_password_reset_email(email)
#             return render_template("reset_password_done.html") 
#         except Exception as e:
#             print("Error occurred: ", e)
#             return render_template("reset_password.html", error="An error occurred. Please try again.")  
#     else:
#         return render_template("reset_password.html") 


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
            print(session['uid'])

            # Retrieve the document from Firestore
            doc_ref = db.collection('users').document(session['uid'])
            doc_snapshot = doc_ref.get()

            # Check if the document exists and extract user data
            if doc_snapshot.exists:
                doc_data = doc_snapshot.to_dict()
                print("Document Data:", doc_data)  # Print all fields in the document
                
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
    return render_template("login.html", message="Logout successful")

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)

