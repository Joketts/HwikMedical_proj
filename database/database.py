import sqlite3
from geopy.distance import geodesic

#Sets up patient records database
def init_db():
    conn_patient = sqlite3.connect('database/patient_records.db')
    cursor_patient = conn_patient.cursor()
    cursor_patient.execute('''CREATE TABLE IF NOT EXISTS patient_records (
        id INTEGER PRIMARY KEY,
        name TEXT,
        nhs_number TEXT UNIQUE,
        address TEXT,
        conditions TEXT,
        actions TEXT NULL 
    )''')
    conn_patient.commit()
    conn_patient.close()

#Adds patient data from incoming incident reports, updating conditions as a list of strings unless its the first time
def add_new_incident(name, nhs_number, address, condition):
    # Update patient records with the new condition
    conn_patient = sqlite3.connect('database/patient_records.db')
    cursor_patient = conn_patient.cursor()
    cursor_patient.execute("SELECT conditions FROM patient_records WHERE nhs_number = ?", (nhs_number,))
    patient_result = cursor_patient.fetchone()

    if patient_result:
        current_conditions = patient_result[0]
        updated_conditions = f"{current_conditions}, {condition}"
        cursor_patient.execute("UPDATE patient_records SET conditions = ? WHERE nhs_number = ?",
                               (updated_conditions, nhs_number))
    else:
        cursor_patient.execute("INSERT INTO patient_records (name, nhs_number, address, conditions) VALUES (?, ?, ?, ?)",
                               (name, nhs_number, address, condition))

    conn_patient.commit()
    conn_patient.close()

#gets lon lat for finding nearest hospital
def get_hospitals():
    conn = sqlite3.connect('database/scottish_hospitals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, latitude, longitude FROM hospitals")
    hospitals = cursor.fetchall()
    conn.close()
    return hospitals

#finds nearest hospital for rescue request
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

#rescue request database not needed

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

#again just for testing
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

if __name__ == '__main__':
    init_db()
    print("Database made")
