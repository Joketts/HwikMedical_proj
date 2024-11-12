import requests

def get_patient_info():
    nhs_number = input("Enter NHS number: ")
    response = requests.post('http://127.0.0.1:5000/patient_info', json={"nhs_number": nhs_number})
    if response.status_code == 200:
        print("Patient information:", response.json()["data"])
    else:
        print("Error:", response.json()["message"])

    if response.status_code == 200:
        try:
            print("Patient information:", response.json()["data"])
        except (ValueError, KeyError) as e:
            print("Error parsing JSON response:", e)
    else:
        print("Error:", response.text or response.reason)


def add_new_incident():
    name = input("Enter patient name: ")
    nhs_number = input("Enter NHS number: ")
    address = input("Enter incident address: ")
    condition = input("Enter patients incident condition: ")

    response = requests.post('http://127.0.0.1:5000/add_incident', json={
        "name": name,
        "nhs_number": nhs_number,
        "address": address,
        "condition": condition
    })

    if response.status_code == 201:
        print("Patient added successfully.")
    else:
        print("Error:", response.json()["message"])


# TeleOp.py
def list_all_patients():
    response = requests.get('http://127.0.0.1:5000/list_patients')
    if response.status_code == 200:
        patients = response.json()["patients"]
        for patient in patients:
            print(f"ID: {patient[0]}, Name: {patient[1]}, NHS Number: {patient[2]}, Address: {patient[3]}, Condition: {patient[4]}")
    else:
        print("Error fetching patients list.")


def delete_patient():
    nhs_number = input("Enter NHS number of the patient to delete: ")

    response = requests.delete('http://127.0.0.1:5000/delete_patient', json={"nhs_number": nhs_number})

    if response.status_code == 200:
        print("Patient deleted successfully.")
    else:
        print("Error:", response.json().get("message", "Unknown error"))


if __name__ == '__main__':
    action = input("Enter '1' to retrieve patient info, '2' New incident, '3' to list all patients, '4' to update a patient, '5' to delete a patient: ")
    if action == '1':
        get_patient_info()
    elif action == '2':
        add_new_incident()
    elif action == '3':
        list_all_patients()
    elif action == '4':
        delete_patient()
    else:
        print("Invalid choice.")
