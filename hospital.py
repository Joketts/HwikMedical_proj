from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import requests

# Initialize the Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'your_secret_key'
# Database paths
PATIENT_RECORDS_DB = 'database/patient_records.db'

rescue_requests_storage = []
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        hospital_name = request.form['hospital_name']
        password = request.form['password']

        # Validate login credentials
        conn = sqlite3.connect("database/scottish_hospitals.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hospitals WHERE name = ? AND password = ?", (hospital_name, password))
        hospital = cursor.fetchone()
        conn.close()

        if hospital:
            session['hospital_name'] = hospital_name  # Store logged-in hospital in session
            return redirect(url_for('navigation'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('hospital_login.html')

@app.route('/navigation')
def navigation():
    if 'hospital_name' not in session:
        return redirect(url_for('login'))

    hospital_name = session['hospital_name']
    return render_template('hospital_navigation.html', hospital_name=hospital_name)

@app.route('/dashboard')
def dashboard():
    if 'hospital_name' not in session:
        return redirect(url_for('login'))

    hospital_name = session['hospital_name']
    return render_template('hospital_rescue_requests.html', hospital_name=hospital_name)


@app.route('/patient_records')
def patient_records():
    if 'hospital_name' not in session:
        return redirect(url_for('login'))

    return render_template('hospital_index.html')



@app.route('/api/hospital_rescue_requests', methods=['GET'])
def get_hospital_rescue_requests():
    if 'hospital_name' not in session:
        return jsonify({"error": "Not authorized"}), 401

    hospital_name = session['hospital_name']
    filtered_requests = [req for req in rescue_requests_storage if req['hospital_name'] == hospital_name]
    return jsonify(filtered_requests)

@app.route('/logout')
def logout():
    session.pop('hospital_name', None)
    return redirect(url_for('login'))

# Route to receive rescue requests
@app.route('/receive_rescue_request', methods=['POST'])
def receive_rescue_request():
    data = request.json
    nhs_number = data.get("nhs_number")
    patient_condition = data.get("condition")
    print(f"Received rescue request for NHS Number: {nhs_number} with condition: {patient_condition}")

    # Add to global storage for dashboard display
    rescue_requests_storage.append(data)
    # Retrieve patient data from the database
    patient_data = get_patient_data(nhs_number)

    if patient_data:
        print(f"Patient found: {patient_data[1]} (NHS Number: {patient_data[2]})")

        # Combine patient data with the rescue request
        response_data = {
            "message": "Rescue request received successfully",
            "rescue_request": data,
            "patient_data": {
                "name": patient_data[1],
                "nhs_number": patient_data[2],
                "address": patient_data[3],
                "conditions": patient_data[4],
            },
        }

        # Send data to the ambulance service
        send_to_ambulance(response_data["patient_data"], data)

        return jsonify(response_data), 200
    else:
        print(f"No patient found for NHS Number: {nhs_number}")
        return jsonify({"message": "Patient not found"}), 404

# Retrieve patient data from the database
def get_patient_data(nhs_number):
    conn = sqlite3.connect(PATIENT_RECORDS_DB)
    cursor = conn.cursor()

    # Query patient data by NHS number
    cursor.execute("SELECT * FROM patient_records WHERE nhs_number = ?", (nhs_number,))
    patient_data = cursor.fetchone()

    conn.close()
    return patient_data

#send data to ambulance

AMBULANCE_SERVICE_URL = "http://127.0.0.1:5003/receive_medical_records"

def send_to_ambulance(patient_data, rescue_request):
    print(f"Sending data to ambulance service...")
    try:
        response = requests.post(AMBULANCE_SERVICE_URL, json={
            "patient_data": patient_data,
            "rescue_request": rescue_request
        })
        if response.status_code == 200:
            print("Ambulance service responded successfully.")
        else:
            print(f"Error from ambulance service: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Failed to communicate with ambulance service: {e}")



#api endpoints for front end data

@app.route('/api/rescue_requests', methods=['GET'])
def get_rescue_requests():
    # Serve rescue requests from the in-memory storage
    return jsonify(rescue_requests_storage)


@app.route('/api/patient_records', methods=['GET'])
def get_patient_records():
    conn = sqlite3.connect(PATIENT_RECORDS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name, nhs_number, address, conditions, actions FROM patient_records")
    patient_records = [
        {
            "name": row[0],
            "nhs_number": row[1],
            "address": row[2],
            "conditions": row[3],
            "actions": row[4] or "No actions recorded"  # Default message if actions is NULL
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(patient_records)

@app.route('/update_callout', methods=['POST'])
def update_callout():
    data = request.json
    nhs_number = data.get('nhs_number')
    actions = data.get('actions')
    reg_number = data.get('registration_number')

    # Update the patient record with the provided actions
    conn = sqlite3.connect(PATIENT_RECORDS_DB)
    cursor = conn.cursor()

    # Retrieve the existing actions for the patient
    cursor.execute("SELECT actions FROM patient_records WHERE nhs_number = ?", (nhs_number,))
    result = cursor.fetchone()

    if result:
        existing_actions = result[0]  # Existing actions as a string
        if existing_actions:
            updated_actions = f"{existing_actions}, {actions}"  # Append new action
        else:
            updated_actions = actions  # First action if no existing ones

        # Update the actions field in the database
        cursor.execute(
            "UPDATE patient_records SET actions = ? WHERE nhs_number = ?",
            (updated_actions, nhs_number)
        )
        conn.commit()
        print(f"Updated actions for NHS Number {nhs_number}: {updated_actions}")
        conn.close()
        return jsonify({"message": "Patient record updated successfully"}), 200
    else:
        conn.close()
        print(f"No patient found with NHS Number {nhs_number}")
        return jsonify({"message": "Patient record not found"}), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
