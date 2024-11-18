import sqlite3
from geopy.distance import geodesic

DATABASE_PATH_INCIDENT = 'database/incident_report.db'
DATABASE_PATH_PATIENT = 'database/patient_records.db'

def init_db():
    # Initialize incident report database
    conn_incident = sqlite3.connect(DATABASE_PATH_INCIDENT)
    cursor_incident = conn_incident.cursor()
    cursor_incident.execute('''CREATE TABLE IF NOT EXISTS incident_report (
        id INTEGER PRIMARY KEY,
        name TEXT,
        nhs_number TEXT UNIQUE,
        incident_address TEXT,
        condition TEXT
    )''')
    conn_incident.commit()
    conn_incident.close()

    # Initialize patient records database
    conn_patient = sqlite3.connect(DATABASE_PATH_PATIENT)
    cursor_patient = conn_patient.cursor()
    cursor_patient.execute('''CREATE TABLE IF NOT EXISTS patient_records (
        id INTEGER PRIMARY KEY,
        name TEXT,
        nhs_number TEXT UNIQUE,
        address TEXT,
        conditions TEXT
        actions TEXT DEFAULT NULL
    )''')
    conn_patient.commit()
    conn_patient.close()

def add_new_incident(name, nhs_number, address, condition):
    conn_incident = sqlite3.connect(DATABASE_PATH_INCIDENT)
    cursor_incident = conn_incident.cursor()

    # Check if an entry with the same NHS number already exists in incident report
    cursor_incident.execute("SELECT condition FROM incident_report WHERE nhs_number = ?", (nhs_number,))
    incident_result = cursor_incident.fetchone()

    if incident_result:
        # Replace the existing condition with the new one
        cursor_incident.execute("UPDATE incident_report SET condition = ?, incident_address = ? WHERE nhs_number = ?",
                                (condition, address, nhs_number))
    else:
        # Insert a new incident if it doesn't exist
        cursor_incident.execute("INSERT INTO incident_report (name, nhs_number, incident_address, condition) VALUES (?, ?, ?, ?)",
                                (name, nhs_number, address, condition))

    conn_incident.commit()
    conn_incident.close()

    # Update patient records with the new condition
    conn_patient = sqlite3.connect(DATABASE_PATH_PATIENT)
    cursor_patient = conn_patient.cursor()
    cursor_patient.execute("SELECT conditions FROM patient_records WHERE nhs_number = ?", (nhs_number,))
    patient_result = cursor_patient.fetchone()

    if patient_result:
        # Add the new condition to the existing list of conditions
        current_conditions = patient_result[0]
        updated_conditions = f"{current_conditions}, {condition}"
        cursor_patient.execute("UPDATE patient_records SET conditions = ? WHERE nhs_number = ?",
                               (updated_conditions, nhs_number))
    else:
        # Insert a new patient record if it doesn't exist
        cursor_patient.execute("INSERT INTO patient_records (name, nhs_number, address, conditions) VALUES (?, ?, ?, ?)",
                               (name, nhs_number, address, condition))

    conn_patient.commit()
    conn_patient.close()

# gets incident patient record
def get_patient_by_nhs(nhs_number):
    conn = sqlite3.connect('database/incident_report.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE nhs_number = ?", (nhs_number,))
    result = cursor.fetchone()
    conn.close()
    return result
# lists incident patients


#hospital_code

def get_hospitals():
    conn = sqlite3.connect('database/scottish_hospitals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, latitude, longitude FROM hospitals")
    hospitals = cursor.fetchall()
    conn.close()
    return hospitals


def find_nearest_hospital(incident_location):
    hospitals = get_hospitals()
    nearest_hospital = None
    shortest_distance = float('inf')

    for hospital in hospitals:
        hospital_id, name, latitude, longitude = hospital
        hospital_location = (latitude, longitude)
        distance = geodesic(incident_location, hospital_location).kilometers

        if distance < shortest_distance:
            shortest_distance = distance
            nearest_hospital = {
                "id": hospital_id,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "distance": distance
            }

    return nearest_hospital

#rescue request database

def init_rescue_requests_db():
    conn = sqlite3.connect('database/rescue_requests.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS rescue_requests (
        id INTEGER PRIMARY KEY,
        patient_name TEXT,
        nhs_number TEXT,
        condition TEXT,
        incident_address TEXT,
        incident_latitude REAL,
        incident_longitude REAL,
        hospital_id INTEGER,
        hospital_name TEXT,
        hospital_latitude REAL,
        hospital_longitude REAL,
        distance_to_hospital REAL,
        status TEXT DEFAULT 'Pending'
    )''')
    conn.commit()
    conn.close()

def save_rescue_request(request_data):
    conn = sqlite3.connect('database/rescue_requests.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO rescue_requests 
        (patient_name, nhs_number, condition, incident_address, incident_latitude, 
         incident_longitude, hospital_id, hospital_name, hospital_latitude, 
         hospital_longitude, distance_to_hospital, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            request_data["patient_name"],
            request_data["nhs_number"],
            request_data["condition"],
            request_data["incident_address"],
            request_data["incident_location"][0],
            request_data["incident_location"][1],
            request_data["hospital_id"],
            request_data["hospital_name"],
            request_data["hospital_location"][0],
            request_data["hospital_location"][1],
            request_data["distance_to_hospital"],
            request_data["status"]
        ))
    conn.commit()
    conn.close()

def update_request_status(request_id, status):
    conn = sqlite3.connect('database/rescue_requests.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE rescue_requests SET status = ? WHERE id = ?", (status, request_id))
    conn.commit()
    conn.close()



if __name__ == '__main__':
    init_db()
    print("Database made")
