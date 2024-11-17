from flask import Flask, jsonify, request, render_template

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
    pending_callouts = [callout for callout in callouts if callout["status"] == "Pending"]
    print(f"Serving call-outs: {pending_callouts}")  # Debugging print statement
    return jsonify(pending_callouts)

@app.route('/ambulance/accept_callout', methods=['POST'])
def accept_callout():
    data = request.json
    callout_id = data.get('id')
    reg_number = data.get('registration_number')

    for callout in callouts:
        if callout['id'] == callout_id and callout['status'] == "Pending":
            callout['status'] = "Accepted"
            callout['ambulance'] = reg_number
            return jsonify({"message": f"Call-out {callout_id} accepted by ambulance {reg_number}"})

    return jsonify({"message": "Call-out not found or already accepted"}), 400


if __name__ == '__main__':
    print("Ambulance service is running on port 5003...")
    app.run(host='0.0.0.0', port=5003)

