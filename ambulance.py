from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# storage for callouts
callouts = []

# storage for signed in ambulance (wasn't used)
ambulances = []

# renders log in page
@app.route('/')
def login_page():
    return render_template('ambulance_login.html')

# renders callouts page
@app.route('/index')
def index():
    return render_template('ambulance_index.html')

# handles login request
@app.route('/ambulance/login', methods=['POST'])
def login():
    data = request.json
    reg_number = data.get('registration_number')
    if reg_number:
        # adds reg number to global list (wasn't used)
        ambulances.append(reg_number)
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid registration number"}), 400

# gets the patient medical records from the request send from hospital is a combination of
# rescue request and patient_data
@app.route('/receive_medical_records', methods=['POST'])
def receive_medical_records():
    data = request.json
    patient_data = data.get("patient_data")
    rescue_request = data.get("rescue_request")

    if patient_data and rescue_request:
        callout = {
            "id": len(callouts) + 1,
            "patient_name": patient_data["name"],
            "nhs_number": patient_data["nhs_number"],
            "condition": rescue_request["condition"],
            "incident_address": rescue_request["incident_address"],
            "status": "Pending",
        }
        callouts.append(callout)

        print(f"Call-out added: {callout}")

        return jsonify({"message": "Medical records received and stored successfully"}), 200
    else:
        print("Error: Missing patient data or rescue request details.")
        return jsonify({"message": "Invalid data received"}), 400


# only shows call-outs with Pending status
@app.route('/ambulance/callouts', methods=['GET'])
def get_callouts():
    # Serve call-outs with "Pending" or "Pending Actions" status
    relevant_callouts = [
        callout for callout in callouts if callout["status"] in ["Pending", "Pending Actions"]
    ]
    print(f"Serving call-outs: {relevant_callouts}")
    return jsonify(relevant_callouts)

# handles accepting of callouts, updating status to taken when accepted and sending that back to hospital
@app.route('/ambulance/accept_callout', methods=['POST'])
def accept_callout():
    data = request.json
    callout_id = data.get('id')
    reg_number = data.get('registration_number')

    callout = next((c for c in callouts if c["id"] == callout_id), None)

    if callout and callout["status"] == "Pending":
        callout["status"] = "Pending Actions"
        callout["ambulance"] = reg_number

        try:
            response = requests.post('http://127.0.0.1:5001/update_request_status', json={
                "nhs_number": callout["nhs_number"],
                "status": "Taken",
            })
            if response.status_code == 200:
                print(f"Hospital notified successfully for call-out {callout_id}")
            else:
                print(f"Failed to notify hospital: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error communicating with hospital: {e}")

        return jsonify({"message": f"Call-out {callout_id} accepted"}), 200

    return jsonify({"message": "Call-out not found or already taken"}), 400

# renders callout details page of accepted callout for actions to be inputted
@app.route('/ambulance/actions/<int:callout_id>', methods=['GET'])
def action_page(callout_id):
    callout = next((c for c in callouts if c["id"] == callout_id), None)
    if callout:
        return render_template('callout_details.html', callout=callout)
    else:
        return jsonify({"message": "Call-out not found"}), 404

# submits action taken back to the hospital to update patient records, and updates rescue request status also sent to hospital
@app.route('/ambulance/submit_actions', methods=['POST'])
def submit_actions():
    data = request.json
    callout_id = int(data.get('id'))
    actions = data.get('actions')
    reg_number = data.get('registration_number')

    callout = next((c for c in callouts if c["id"] == callout_id), None)

    if callout and callout["status"] == "Pending Actions":
        callout["actions"] = actions
        callout["status"] = "Completed"

        print(f"Submitting actions for call-out {callout_id}: {actions}")

        try:
            response = requests.post('http://127.0.0.1:5001/update_request_status', json={
                "nhs_number": callout["nhs_number"],
                "status": "Completed",
            })
            if response.status_code != 200:
                print("Failed to notify hospital about status update")
        except Exception as e:
            print(f"Error notifying hospital about status update: {e}")

        try:
            response = requests.post("http://127.0.0.1:5001/update_callout", json={
                "nhs_number": callout["nhs_number"],
                "actions": actions,
                "registration_number": reg_number,
            })
            if response.status_code == 200:
                return jsonify({"message": "Actions submitted successfully to the hospital server"})
            else:
                return jsonify({"message": "Failed to update hospital server"}), 500
        except Exception as e:
            print(f"Error sending actions to hospital server: {e}")
            return jsonify({"message": "Error communicating with hospital server"}), 500

    return jsonify({"message": "Call-out not found or already completed"}), 400

if __name__ == '__main__':
    print("Ambulance service is running on port 5003...")
    app.run(host='0.0.0.0', port=5003)

