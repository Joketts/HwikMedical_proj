function submitIncident() {
    const name = document.getElementById("name").value;
    const nhs_number = document.getElementById("nhs_number").value;
    const address = document.getElementById("address").value;
    const condition = document.getElementById("condition").value;

    fetch('/add_incident', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            nhs_number: nhs_number,
            address: address,
            condition: condition
        })
    })
    .then(response => response.json())
    .then(data => {
        const responseDiv = document.getElementById("response");
        responseDiv.style.display = "block"; // Show the response box

        // Display the main message
        let outputText = `<p>${data.message}</p>`;

        // Check if there's a rescue request and format it
        if (data.rescue_request) {
            const request = data.rescue_request;
            outputText += `
                <p><strong>Rescue Request Details:</strong></p>
                <p>Patient Name: ${request.patient_name}</p>
                <p>NHS Number: ${request.nhs_number}</p>
                <p>Condition: ${request.condition}</p>
                <p>Incident Address: ${request.incident_address}</p>
                <p>Hospital Name: ${request.hospital_name}</p>
                <p>Hospital Location: Latitude ${request.hospital_location[0]}, Longitude ${request.hospital_location[1]}</p>
                <p>Distance to Hospital: ${request.distance_to_hospital.toFixed(2)} km</p>
            `;
        }

        responseDiv.innerHTML = outputText;
    })
    .catch(error => {
        console.error('Error:', error);
        const responseDiv = document.getElementById("response");
        responseDiv.style.display = "block"; // Show the response box
        responseDiv.innerHTML = "<p>Error submitting incident</p>";
    });
}
