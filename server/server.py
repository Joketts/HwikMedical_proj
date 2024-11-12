from flask import Flask, jsonify, request
import sqlite3
from database.database import get_patient_by_nhs, add_new_incident, get_all_patients, delete_patient_from_db, init_db, find_nearest_hospital, init_rescue_requests_db, save_rescue_request, update_request_status
from geopy.geocoders import Nominatim

init_db()
init_rescue_requests_db()
app = Flask(__name__)

geolocator = Nominatim(user_agent="kwikmedical")


@app.route('/add_incident', methods=['POST'])
def add_incident():
    data = request.json
    name = data.get("name")
    nhs_number = data.get("nhs_number")
    address = data.get("address")
    condition = data.get("condition")

    # Geocode the address to get latitude and longitude
    location = geolocator.geocode(address)
    if location:
        incident_location = (location.latitude, location.longitude)

        # Add the incident to the incident database
        add_new_incident(name, nhs_number, address, condition)

        # Find the nearest hospital
        nearest_hospital = find_nearest_hospital(incident_location)

        # Generate the rescue request data
        rescue_request_data = {
            "patient_name": name,
            "nhs_number": nhs_number,
            "condition": condition,
            "incident_address": address,
            "incident_location": incident_location,
            "hospital_id": nearest_hospital["id"],
            "hospital_name": nearest_hospital["name"],
            "hospital_location": (nearest_hospital["latitude"], nearest_hospital["longitude"]),
            "distance_to_hospital": nearest_hospital["distance"],
            "status": "Pending"
        }

        # Save the rescue request
        save_rescue_request(rescue_request_data)

        # Simulate sending the request (for now, just update status to "Sent")
        # Here you could add real sending logic in the future
        rescue_request_data["status"] = "Sent"

        # Optionally update status in the database
        # Retrieve the ID of the last inserted request
        conn = sqlite3.connect('database/rescue_requests.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM rescue_requests ORDER BY id DESC LIMIT 1")
        request_id = cursor.fetchone()[0]
        conn.close()

        update_request_status(request_id, "Sent")

        return jsonify({
            "message": "Rescue request generated and sent",
            "rescue_request": rescue_request_data
        }), 201
    else:
        return jsonify({"message": "Incident address not found"}), 400

@app.route('/list_patients', methods=['GET'])
def list_patients():
    patients = get_all_patients()
    return jsonify({"patients": patients})

@app.route('/delete_patient', methods=['DELETE'])
def delete_patient():
    nhs_number = request.json.get("nhs_number")
    delete_patient_from_db(nhs_number)
    return jsonify({"message": "Patient deleted successfully"})

@app.route('/patient_info', methods=['POST'])
def patient_info():
    data = request.json
    nhs_number = data.get("nhs_number")

    if not nhs_number or not nhs_number.isdigit():
        return jsonify({"message": "Invalid NHS number"}), 400

    patient = get_patient_by_nhs(nhs_number)
    if patient:
        return jsonify({"message": "Patient information", "data": {
            "id": patient[0],
            "name": patient[1],
            "nhs_number": patient[2],
            "address": patient[3],
            "condition": patient[4]
        }})
    else:
        return jsonify({"message": "Patient not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
