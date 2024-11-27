from flask import Flask, jsonify, request, render_template
import sqlite3
from database.database import add_new_incident, init_db, find_nearest_hospital, init_rescue_requests_db, save_rescue_request
from geopy.geocoders import Nominatim
import requests

init_db()
init_rescue_requests_db()
app = Flask(__name__, static_folder="static", template_folder="templates")
geolocator = Nominatim(user_agent="kwikmedical")

# route to main page
@app.route('/')
def index():
    return render_template('index.html')
# route to report page
@app.route('/report_incident')
def report_incident():
    return render_template('report_incident.html')

# generates rescue request
@app.route('/add_incident', methods=['POST'])
def add_incident():
    data = request.json
    name = data.get("name")
    nhs_number = data.get("nhs_number")
    address = data.get("address")
    condition = data.get("condition")

    # geopy to find lon lat for address
    location = geolocator.geocode(address)
    if location:
        incident_location = (location.latitude, location.longitude)

        add_new_incident(name, nhs_number, address, condition)
        # database function to find nearest hospital
        nearest_hospital = find_nearest_hospital(incident_location)

        # generates rescue request
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

        # saves request
        save_rescue_request(rescue_request_data)
        #sends request to sending function
        send_rescue_request_to_hospital(rescue_request_data)
        return jsonify({
            "message": "Rescue request generated and sent",
            "rescue_request": rescue_request_data
        }), 201
    else:
        return jsonify({"message": "Incident address not found"}), 400

#sends request to hospital
def send_rescue_request_to_hospital(rescue_request_data):
    print(f"Sending rescue request to hospital: {rescue_request_data}")
    try:
        response = requests.post("http://127.0.0.1:5001/receive_rescue_request", json=rescue_request_data)
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
