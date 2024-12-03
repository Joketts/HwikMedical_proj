from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import requests


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "key1234"

# global storage for rescue requests
rescue_requests_storage = []

# login page validates against scottish_hospitals database, sends hospital to the navigation page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        hospital_name = request.form['hospital_name']
        password = request.form['password']

        conn = sqlite3.connect("database/scottish_hospitals.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hospitals WHERE name = ? AND password = ?", (hospital_name, password))
        hospital = cursor.fetchone()
        conn.close()

        if hospital:
            session['hospital_name'] = hospital_name
            return redirect(url_for('navigation'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('hospital_login.html')

# navigation page
@app.route('/navigation')
def navigation():
    if 'hospital_name' not in session:
        return redirect(url_for('login'))

    hospital_name = session['hospital_name']
    return render_template('hospital_navigation.html', hospital_name=hospital_name)

# rescue requests page
@app.route('/dashboard')
def dashboard():
    if 'hospital_name' not in session:
        return redirect(url_for('login'))

    hospital_name = session['hospital_name']
    return render_template('hospital_rescue_requests.html', hospital_name=hospital_name)

# patient records page
@app.route('/patient_records')
def patient_records():
    if 'hospital_name' not in session:
        return redirect(url_for('login'))

    return render_template('hospital_index.html')

# log out brings you back to login
@app.route('/logout')
def logout():
    session.pop('hospital_name', None)
    return redirect(url_for('login'))

# endpoint for hospital rescue request fetch, filters rescue requests only allowing for certain hospital
@app.route('/api/hospital_rescue_requests', methods=['GET'])
def get_hospital_rescue_requests():
    if 'hospital_name' not in session:
        return jsonify({"error": "Not authorized"}), 401

    hospital_name = session['hospital_name']
    filtered_requests = [req for req in rescue_requests_storage if req['hospital_name'] == hospital_name]
    return jsonify(filtered_requests)

# receives rescue requests
@app.route('/receive_rescue_request', methods=['POST'])
def receive_rescue_request():
    data = request.json
    nhs_number = data.get("nhs_number")
    patient_condition = data.get("condition")
    print(f"Received rescue request for NHS Number: {nhs_number} with condition: {patient_condition}")

    # adds to global storage for showing requests
    rescue_requests_storage.append(data)
    # Retrieve patient data from the database
    patient_data = get_patient_data(nhs_number)

    if patient_data:
        print(f"Patient found: {patient_data[1]} (NHS Number: {patient_data[2]})")

        # sends both the rescue request and the patient data to the ambulance
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

# gets patient data
def get_patient_data(nhs_number):
    conn = sqlite3.connect('database/patient_records.db')
    cursor = conn.cursor()

    # Query patient data by NHS number
    cursor.execute("SELECT * FROM patient_records WHERE nhs_number = ?", (nhs_number,))
    patient_data = cursor.fetchone()

    conn.close()
    return patient_data

# sends data to ambulance
def send_to_ambulance(patient_data, rescue_request):
    print(f"Sending data to ambulance service...")
    try:
        response = requests.post("http://127.0.0.1:5003/receive_medical_records", json={
            "patient_data": patient_data,
            "rescue_request": rescue_request
        })
        if response.status_code == 200:
            print("Ambulance service responded successfully.")
        else:
            print(f"Error from ambulance service: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Failed to communicate with ambulance service: {e}")

# api endpoints for front end data
@app.route('/api/rescue_requests', methods=['GET'])
def get_rescue_requests():
    return jsonify(rescue_requests_storage)

# api endpoints for front end data
@app.route('/api/patient_records', methods=['GET'])
def get_patient_records():
    conn = sqlite3.connect('database/patient_records.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, nhs_number, address, conditions, actions FROM patient_records")
    patient_records = [
        {
            "name": row[0],
            "nhs_number": row[1],
            "address": row[2],
            "conditions": row[3],
            "actions": row[4] or "No actions recorded"
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(patient_records)

# updates the status of rescue requests
@app.route('/update_request_status', methods=['POST'])
def update_request_status():
    try:
        if not request.is_json:
            return jsonify({"message": "Invalid JSON format"}), 400

        data = request.get_json()
        nhs_number = data.get('nhs_number')
        status = data.get('status')

        if not nhs_number or not status:
            return jsonify({"message": "Missing required fields"}), 400

        for req in rescue_requests_storage:
            if req["nhs_number"] == nhs_number:
                req["status"] = status
                print(f"Updated status for NHS Number {nhs_number} to {status}")
                return jsonify({"message": "Rescue request status updated successfully"}), 200

        print(f"No rescue request found for NHS Number {nhs_number}")
        return jsonify({"message": "Rescue request not found"}), 404
    except Exception as e:
        print(f"Error in /update_request_status: {e}")
        return jsonify({"message": "Internal server error"}), 500


# updates the patient records with actions taken if actions already there adds them as a list of strings
@app.route('/update_callout', methods=['POST'])
def update_callout():
    data = request.json
    nhs_number = data.get('nhs_number')
    actions = data.get('actions')

    conn = sqlite3.connect('database/patient_records.db')
    cursor = conn.cursor()

    cursor.execute("SELECT actions FROM patient_records WHERE nhs_number = ?", (nhs_number,))
    result = cursor.fetchone()

    if result:
        existing_actions = result[0]
        if existing_actions:
            updated_actions = f"{existing_actions}, {actions}"
        else:
            updated_actions = actions

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

# runs app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
