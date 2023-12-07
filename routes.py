# routes.py
from myapp import app, db
from flask import request, render_template, jsonify, redirect, url_for
from .models import Employee, TimeLog
import datetime
from firebase_admin import auth, exceptions, firestore

@app.route('/assignAdmin', methods=['POST'])
def assign_admin():
    uid = request.json.get('uid')
    if uid:
        db = firestore.client()
        db.collection('userRoles').document(uid).set({
            'isAdmin': True
        })
        return jsonify({"message": "User added as admin"}), 200
    else:
        return jsonify({"message": "No uid provided"}), 400

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if email is None or password is None:
            return jsonify({"message": "Email and password are required"}), 400
        if len(password) < 6:
            return jsonify({"message": "Password must be at least 6 characters long"}), 400
        try:
            user = auth.get_user_by_email(email)
            return jsonify({"message": "User with this email already exists"}), 400
        except Exception:
            try:
                user = auth.create_user(email=email, password=password)
                return jsonify({"message": "User created successfully"}), 200
            except exceptions.FirebaseError as e:
                return jsonify({"message": "User creation failed", "error": str(e)}), 400
    else:
        return render_template('signup.html')
    
from flask import request
from firebase_admin import auth, firestore

@app.route('/dashboard')
def dashboard():
    # Check if the Authorization header is present
    if 'Authorization' not in request.headers:
        return "Unauthorized", 401

    # Get the ID token from the Authorization header
    id_token = request.headers['Authorization'].split(' ').pop()
    print('ID token:', id_token)  # Log the ID token

    # Verify the ID token and get the user's Firebase UID
    try:
        decoded_token = auth.verify_id_token(id_token)
    except Exception as e:
        print('Verify ID token error:', e)  # Log the verify ID token error
        return "Unauthorized", 401

    uid = decoded_token['uid']
    print('Firebase UID:', uid)  # Log the Firebase UID

    # Check if the current user is an admin
    db = firestore.client()
    user_role_doc = db.collection('userRoles').document(uid).get()
    is_admin = user_role_doc.exists and user_role_doc.to_dict().get('isAdmin', False)
    print('Is admin:', is_admin)  # Log whether the user is an admin

    # Get all users if the current user is an admin
    users = []
    if is_admin:
        users = auth.list_users().iterate_all()
        # Limit the information that is returned for each user
        users = [{'uid': user.uid, 'email': user.email} for user in users]
    # Pass the is_admin and users variables to the template
    return render_template('dashboard.html', is_admin=is_admin, users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if email is None or password is None:
            return jsonify({"message": "Email and password are required"}), 400
        try:
            user = auth.get_user_by_email(email)
            # Firebase should handle user sessions, no need to store email in session
            return jsonify({"message": "User logged in successfully"}), 200
        except exceptions.FirebaseError as e:
            return jsonify({"message": "Login failed", "error": str(e)}), 400
    else:
        return render_template('login.html')

@app.route('/clock_in', methods=['POST'])
def clock_in():
    employee_id = request.form.get('employee_id')
    clock_in_time = datetime.datetime.now()
    time_log = TimeLog(clock_in_time=clock_in_time, employee_id=employee_id)
    db.session.add(time_log)
    db.session.commit()
    return {"message": "Clock in successful"}, 200

@app.route('/clock_out', methods=['POST'])
def clock_out():
    employee_id = request.form.get('employee_id')
    clock_out_time = datetime.datetime.now()
    time_log = TimeLog.query.filter_by(employee_id=employee_id).order_by(TimeLog.clock_in_time.desc()).first()
    if time_log and not time_log.clock_out_time:
        time_log.clock_out_time = clock_out_time
        db.session.commit()
        return {"message": "Clock out successful"}, 200
    else:
        return {"message": "Invalid clock out"}, 400

@app.route('/assignRole', methods=['POST'])
def assign_role():
    id_token = request.json.get('idToken')
    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    auth.set_custom_user_claims(uid, {'admin': True})
    return {"message": "Admin role assigned successfully"}, 200