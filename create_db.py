from app import app
from models import db, Admin, Doctor, Patient

# Create database and tables
with app.app_context():
    db.create_all()

    # OPTIONAL: Add default users (only if not exists)

    if not Admin.query.filter_by(username="admin").first():
        admin = Admin(username="admin", password="admin123")
        db.session.add(admin)

    if not Doctor.query.filter_by(username="doctor1").first():
        doctor = Doctor(name="Dr. John",
                        username="doctor1",
                        password="doctor123")
        db.session.add(doctor)

    if not Patient.query.filter_by(username="patient1").first():
        patient = Patient(name="Ravi",
                          username="patient1",
                          password="patient123")
        db.session.add(patient)

    db.session.commit()

print("✅ Database created successfully!")
