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
        let outputText = `<H3>${data.message}</H3>`;

        // Check if there's a rescue request and format it
        if (data.rescue_request) {
            const request = data.rescue_request;
            outputText += `
                <h3>Rescue Request Details:</h3>
                <p><strong>Patient Name: ${request.patient_name}</strong><p>
                <p><strong>NHS Number: ${request.nhs_number}<strong></p>
                <p><strong>Condition: ${request.condition}<strong></p>
                <p><strong>Incident Address: ${request.incident_address}<strong></p>
                <p><strong>Hospital Name: ${request.hospital_name}<strong></p>
                <p><strong>Hospital Location: Latitude ${request.hospital_location[0]}, Longitude ${request.hospital_location[1]}<strong></p>
                <p><strong>Distance to Hospital: ${request.distance_to_hospital.toFixed(2)} km<strong></p>
            `;
        }

        responseDiv.innerHTML = outputText;
        responseDiv.style.display = "block"; // Show the response box
    })
    .catch(error => {
        console.error('Error:', error);
        const responseDiv = document.getElementById("response");
        responseDiv.style.display = "block"; // Show the response box
        responseDiv.innerHTML = "<p>Error submitting incident</p>";
    });
}
