import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from forms import RegistrationForm, LoginForm, TutorApplicationForm, ManagementApplicationForm
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = 'your_secret_key'  


cred_path = "key.json"


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.context_processor
def inject_user():
    return dict(logged_In=True)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/home')
def home():

    if session.get("is_logged_in", False):
        return render_template('home.html', name=session["email"])  # Subject page
    return redirect(url_for('login'))

@app.route('/gallery')
def gallery():
    print(session)

    if session.get("is_logged_in", False):
        return render_template('gallery.html') 
        
    return redirect(url_for('login'))


@app.route('/subject')
def subject():
    print(session)

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
    print(session)

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

@app.route('/logout')
def logout():

    # db.child("users").child(session["uid"]).update({"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")})
    print(session)
    session["is_logged_in"] = False
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.is_submitted():
            email = form.email.data
            name = form.name.data
            surname = form.surname.data
            password = form.password.data
            user = auth.create_user(email=email, password=password)
       
        
            print(user)
            session["uid"] = user.uid
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
            
            try : 
                db.collection("users").document(session["uid"]).set(data)
 
                return redirect(url_for('home'))
            except Exception as e:
                flash(f'Login successful!{e}', 'success')
                


    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data


            
            try : 
                user = auth.get_user_by_email(email)

                print(user.uid)
                # if user.password ==
                # print(user.password)


                session["is_logged_in"] = True
                session['uid'] = user.uid
                session["email"] = email
                
                # doc_ref = db.collection('users').document(user.uid)
                # doc = doc_ref.get()
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                flash(f'Login successful!{e}', 'success')
                
     

    return render_template('login.html', form=form)

# Route for password reset
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        try:
            
            auth.send_password_reset_email(email)
            return render_template("reset_password_done.html") 
        except Exception as e:
            print("Error occurred: ", e)
            return render_template("reset_password.html", error="An error occurred. Please try again.")  
    else:
        return render_template("reset_password.html") 




# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
