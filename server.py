from flask import Flask, jsonify, request, render_template
import sqlite3
from database.database import add_new_incident, init_db, find_nearest_hospital, init_rescue_requests_db, save_rescue_request, update_request_status
from geopy.geocoders import Nominatim
import requests

init_db()
init_rescue_requests_db()
app = Flask(__name__, static_folder="static", template_folder="templates")

geolocator = Nominatim(user_agent="kwikmedical")

@app.route('/')
def index():
    return render_template('index.html')  # Serve the front-end page
@app.route('/report_incident')
def report_incident():
    return render_template('report_incident.html')
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

        send_rescue_request_to_hospital(rescue_request_data)
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


def send_rescue_request_to_hospital(rescue_request_data):
    HOSPITAL_URL = "http://127.0.0.1:5001/receive_rescue_request"
    print(f"Sending rescue request to hospital: {rescue_request_data}")

    try:
        response = requests.post(HOSPITAL_URL, json=rescue_request_data)
        if response.status_code == 200:
            print("Hospital response received successfully:")
            print(response.json())
        else:
            print("Hospital response error:")
            print(response.json())
    except Exception as e:
        print(f"Error communicating with hospital service: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
