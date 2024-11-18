from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# In-memory storage for available call-outs
callouts = []

# In-memory storage for logged-in ambulances
ambulances = []

@app.route('/')
def login_page():
    return render_template('ambulance_login.html')
@app.route('/index')
def index():
    return render_template('ambulance_index.html')

@app.route('/receive_medical_records', methods=['POST'])
def receive_medical_records():
    data = request.json

    # Extract data from the request
    patient_data = data.get("patient_data")
    rescue_request = data.get("rescue_request")

    if patient_data and rescue_request:
        callout = {
            "id": len(callouts) + 1,
            "patient_name": patient_data["name"],
            "nhs_number": patient_data["nhs_number"],
            "condition": rescue_request["condition"],
            "incident_address": rescue_request["incident_address"],
            "priority": rescue_request.get("priority", "Not specified"),
            "status": "Pending",
        }
        callouts.append(callout)

        print(f"Call-out added: {callout}")  # Debugging print statement

        return jsonify({"message": "Medical records received and stored successfully"}), 200
    else:
        print("Error: Missing patient data or rescue request details.")
        return jsonify({"message": "Invalid data received"}), 400

@app.route('/ambulance/login', methods=['POST'])
def login():
    data = request.json
    reg_number = data.get('registration_number')
    if reg_number:
        ambulances.append(reg_number)
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid registration number"}), 400


@app.route('/ambulance/callouts', methods=['GET'])
def get_callouts():
    # Serve call-outs with "Pending" or "Pending Actions" status
    relevant_callouts = [
        callout for callout in callouts if callout["status"] in ["Pending", "Pending Actions"]
    ]
    print(f"Serving call-outs: {relevant_callouts}")  # Debugging print statement
    return jsonify(relevant_callouts)

@app.route('/ambulance/accept_callout', methods=['POST'])
def accept_callout():
    data = request.json
    callout_id = data.get('id')
    reg_number = data.get('registration_number')

    for callout in callouts:
        if callout['id'] == callout_id and callout['status'] == "Pending":
            callout['status'] = "Pending Actions"
            callout['ambulance'] = reg_number
            return jsonify({"message": f"Call-out {callout_id} accepted by ambulance {reg_number}"})

    return jsonify({"message": "Call-out not found or already accepted"}), 400

@app.route('/ambulance/actions/<int:callout_id>', methods=['GET'])
def action_page(callout_id):
    # Find the call-out details to display
    callout = next((c for c in callouts if c["id"] == callout_id), None)
    if callout:
        return render_template('callout_details.html', callout=callout)
    else:
        return jsonify({"message": "Call-out not found"}), 404

HOSPITAL_SERVER_URL = "http://127.0.0.1:5001/update_callout"

@app.route('/ambulance/submit_actions', methods=['POST'])
def submit_actions():
    data = request.json
    callout_id = int(data.get('id'))
    actions = data.get('actions')
    reg_number = data.get('registration_number')

    # Find the call-out in the current list
    callout = next((c for c in callouts if c["id"] == callout_id), None)

    if callout:
        # Ensure the call-out is in "Pending Actions" status before completing
        if callout["status"] == "Pending Actions":
            callout["actions"] = actions
            callout["status"] = "Completed"

            print(f"Submitting actions for call-out {callout_id}: {actions}")

            # Send actions to the hospital server
            try:
                response = requests.post(HOSPITAL_SERVER_URL, json={
                    "id": callout_id,
                    "actions": actions,
                    "registration_number": reg_number,
                })
                if response.status_code == 200:
                    print(f"Hospital server updated successfully for call-out {callout_id}")
                    return jsonify({"message": "Actions submitted successfully to the hospital server"})
                else:
                    print(f"Hospital server returned error: {response.status_code}")
                    return jsonify({"message": "Failed to update hospital server"}), 500
            except Exception as e:
                print(f"Error sending actions to hospital server: {e}")
                return jsonify({"message": "Error communicating with hospital server"}), 500
        elif callout["status"] == "Completed":
            return jsonify({"message": "Call-out already completed"}), 400

    return jsonify({"message": "Call-out not found"}), 400

if __name__ == '__main__':
    print("Ambulance service is running on port 5003...")
    app.run(host='0.0.0.0', port=5003)

