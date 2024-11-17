from flask import Flask, jsonify, request, render_template
import sqlite3
import requests

# Initialize the Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Database paths
PATIENT_RECORDS_DB = 'database/patient_records.db'

@app.route('/')
def dashboard():
    return render_template('hospital_index.html')

#for front end storage
rescue_requests_storage = []

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
    cursor.execute("SELECT name, nhs_number, address, conditions FROM patient_records")
    patient_records = [{"name": row[0], "nhs_number": row[1], "address": row[2], "conditions": row[3]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(patient_records)



# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
