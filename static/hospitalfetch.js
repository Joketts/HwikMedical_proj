
// Fetch and update patient records
function fetchPatientRecords() {
    fetch('/api/patient_records')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#patient-records tbody');
            tableBody.innerHTML = ''; // Clear existing rows

            data.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.name}</td>
                    <td>${record.nhs_number}</td>
                    <td>${record.address}</td>
                    <td>${record.conditions}</td>
                `;
                tableBody.appendChild(row);
            });
        });
}

// Fetch and update rescue requests for logged-in hospital
function fetchRescueRequests() {
    fetch('/api/hospital_rescue_requests')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#rescue-requests tbody');
            tableBody.innerHTML = ''; // Clear existing rows

            data.forEach(request => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${request.patient_name}</td>
                    <td>${request.nhs_number}</td>
                    <td>${request.condition}</td>
                    <td>${request.incident_address}</td>
                    <td>${request.status}</td>
                    <td>${request.distance_to_hospital.toFixed(2)} km</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching rescue requests:', error));
}


// Fetch data periodically
setInterval(() => {
    fetchRescueRequests();
    fetchPatientRecords();
}, 5000); // Update every 5 seconds
