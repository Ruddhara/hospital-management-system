from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import random

from models import db, Admin, Doctor, Patient, Pharmacy, Chat, Prescription

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login_patient"
login_manager.init_app(app)

# =============================
# USER LOADER
# =============================
@login_manager.user_loader
def load_user(user_id):
    return Patient.query.get(int(user_id)) or \
           Doctor.query.get(int(user_id)) or \
           Admin.query.get(int(user_id)) or \
           Pharmacy.query.get(int(user_id))


# =============================
# HOME
# =============================
@app.route('/')
def home():
    return render_template("index.html")


# =============================
# LOGIN ROUTES
# =============================
@app.route('/login/patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        user = Patient.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            login_user(user)
            return redirect(url_for('patient_dashboard'))
        flash("Invalid Patient Login")
    return render_template("login_patient.html")


@app.route('/login/doctor', methods=['GET', 'POST'])
def login_doctor():
    if request.method == 'POST':
        user = Doctor.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            login_user(user)
            return redirect(url_for('doctor_dashboard'))
        flash("Invalid Doctor Login")
    return render_template("login_doctor.html")


@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        user = Admin.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash("Invalid Admin Login")
    return render_template("login_admin.html")


@app.route('/login/pharmacy', methods=['GET', 'POST'])
def login_pharmacy():
    if request.method == 'POST':
        user = Pharmacy.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            login_user(user)
            return redirect(url_for('pharmacy_dashboard'))
        flash("Invalid Pharmacy Login")
    return render_template("login_pharmacy.html")


# =============================
# DASHBOARDS
# =============================
@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    doctors = Doctor.query.all()
    return render_template("patient_dashboard.html", doctors=doctors)


@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    return render_template("doctor_dashboard.html")


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    pharmacies = Pharmacy.query.all()
    prescriptions = Prescription.query.all()

    return render_template(
        "admin_dashboard.html",
        doctors=doctors,
        patients=patients,
        pharmacies=pharmacies,
        prescriptions=prescriptions,
        total_doctors=len(doctors),
        total_patients=len(patients),
        total_pharmacies=len(pharmacies),
        total_prescriptions=len(prescriptions)
    )


@app.route('/pharmacy_dashboard')
@login_required
def pharmacy_dashboard():
    return render_template("pharmacy_dashboard.html")


# =============================
# ADD DOCTOR (FIXED ERROR)
# =============================
@app.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        new_doctor = Doctor(
            name=request.form['name'],
            username=request.form['username'],
            password=request.form['password'],
            specialization=request.form['specialization'],
            status=request.form['status']
        )
        db.session.add(new_doctor)
        db.session.commit()
        flash("Doctor added successfully!")
        return redirect(url_for('admin_dashboard'))

    return render_template("add_doctor.html")


# =============================
# CHAT ROUTE
# =============================
@app.route('/chat/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def chat(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    patient = current_user

    if request.method == 'POST':
        message = request.form['message']

        # Save patient message
        chat = Chat(
            patient_id=patient.id,
            doctor_id=doctor.id,
            sender="patient",
            message=message
        )
        db.session.add(chat)

        # AI reply
        ai_reply = generate_ai_reply(message)

        ai_chat = Chat(
            patient_id=patient.id,
            doctor_id=doctor.id,
            sender="ai",
            message=ai_reply
        )
        db.session.add(ai_chat)

        db.session.commit()
        return redirect(url_for('chat', doctor_id=doctor.id))

    chats = Chat.query.filter_by(
        patient_id=patient.id,
        doctor_id=doctor.id
    ).order_by(Chat.timestamp.asc()).all()

    return render_template("chat.html", doctor=doctor, chats=chats)


# =============================
# SIMPLE AI FUNCTION
# =============================
def generate_ai_reply(message):
    message = message.lower()

    if "fever" in message:
        return "You might have viral fever. Stay hydrated and monitor temperature."
    elif "headache" in message:
        return "Headache can be due to stress or dehydration."
    elif "cough" in message:
        return "Persistent cough requires medical evaluation."
    else:
        responses = [
            "Please describe your symptoms clearly.",
            "Consult the doctor for proper diagnosis.",
            "Kindly book an appointment if condition worsens."
        ]
        return random.choice(responses)


# =============================
# LOGOUT
# =============================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# =============================
# RUN APP
# =============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)